#!/usr/bin/env python3
"""Update conference deadlines from official conference websites."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "_data" / "conference_deadlines.json"
USER_AGENT = "ShawnshanksGui conference deadline monitor/1.0"

CONFERENCES = [
    {
        "id": "sigcomm",
        "name": "ACM SIGCOMM",
        "area": "Networking",
        "urls": ["https://conferences.sigcomm.org/sigcomm/{year}/"],
        "aec_urls": [
            "https://conferences.sigcomm.org/sigcomm/{year}/artifact-evaluation/"
        ],
    },
    {
        "id": "nsdi",
        "name": "USENIX NSDI",
        "area": "Networked Systems",
        "urls": ["https://www.usenix.org/conference/nsdi{yy}/call-for-papers"],
        "aec_urls": [
            "https://www.usenix.org/conference/nsdi{yy}/call-for-artifacts"
        ],
    },
    {
        "id": "osdi",
        "name": "USENIX OSDI",
        "area": "Operating Systems",
        "urls": ["https://www.usenix.org/conference/osdi{yy}/call-for-papers"],
        "aec_urls": [
            "https://www.usenix.org/conference/osdi{yy}/call-for-artifacts"
        ],
    },
    {
        "id": "sosp",
        "name": "ACM SOSP",
        "area": "Operating Systems",
        "urls": [
            "https://www.sosp.org/{year}/",
            "https://www.sosp.org/",
        ],
        "aec_urls": ["https://sysartifacts.github.io/sosp{year}/aec-call"],
    },
    {
        "id": "atc",
        "name": "ACM ATC",
        "area": "Systems",
        "urls": [
            "https://sigops.org/s/conferences/atc/{year}/cfp.html",
        ],
        "aec_urls": [
            "https://sysartifacts.github.io/atc{year}/aec-call"
        ],
    },
    {
        "id": "eurosys",
        "name": "ACM EuroSys",
        "area": "Systems",
        "urls": ["https://{year}.eurosys.org/cfp.html"],
        "aec_urls": [
            "https://sysartifacts.github.io/eurosys{year}/aec-call"
        ],
    },
    {
        "id": "asplos",
        "name": "ACM ASPLOS",
        "area": "Architecture & Systems",
        "urls": ["https://www.asplos-conference.org/asplos{year}/cfp/"],
        "aec_urls": [
            "https://www.asplos-conference.org/asplos{year}/for-reviewers/"
        ],
    },
    {
        "id": "conext",
        "name": "ACM CoNEXT",
        "area": "Networking",
        "urls": [
            "https://conferences2.sigcomm.org/co-next/{year}/partials/cfp.html"
        ],
        "tpc_urls": [
            "https://conferences2.sigcomm.org/co-next/{year}/partials/shadow.html"
        ],
        "aec_urls": [
            "https://conferences2.sigcomm.org/co-next/{year}/partials/call_for_artifactcommittee.html"
        ],
        "public_url": "https://conferences.sigcomm.org/co-next/{year}/#!/cfp",
        "tpc_public_url": "https://conferences.sigcomm.org/co-next/{year}/#!/shadow",
        "aec_public_url": "https://conferences.sigcomm.org/co-next/{year}/#!/cfaec",
    },
]

DATE_PATTERN = re.compile(
    r"\b(?:"
    r"(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+)?"
    r"(?:"
    r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+\d{1,2}(?:st|nd|rd|th)?(?:,)?\s+20\d{2}"
    r"|"
    r"\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+20\d{2}"
    r")\b",
    re.IGNORECASE,
)
DEADLINE_TERMS = re.compile(
    r"\b(?:abstract(?: registrations?)?|paper titles? and abstracts?|"
    r"full paper(?: submissions?)?|complete paper submissions?|"
    r"main conference paper submission|paper submission|submission deadline)\b",
    re.IGNORECASE,
)
NOMINATION_TERMS = re.compile(
    r"\b(?:call for (?:shadow )?tpc members"
    r"|(?:tpc|technical program committee|program committee|reviewer)"
    r"[\w\s/-]{0,45}(?:self[- ]nomination|nomination form|volunteer to serve)"
    r"|(?:self[- ]nomination|nominate yourself)[\w\s/-]{0,45}"
    r"(?:tpc|technical program committee|program committee|reviewer))\b",
    re.IGNORECASE,
)
RELATED_TPC_LINK = re.compile(
    r"\b(?:tpc|technical program committee|program committee|"
    r"self[- ]nomination|nomination)\b",
    re.IGNORECASE,
)
AEC_ROLE_TERMS = re.compile(
    r"\b(?:artifact evaluation committee|artifact evaluators?|"
    r"artifact reviewers?|AEC)\b",
    re.IGNORECASE,
)
AEC_ACTION_TERMS = re.compile(
    r"\b(?:self[- ]nomination|nomination (?:page|form)|apply now|"
    r"how to apply|call for evaluators|interested in reviewing artifacts|"
    r"join the artifact evaluation committee)\b",
    re.IGNORECASE,
)
HOTCRP_URL_PATTERN = re.compile(
    r"https?://[A-Za-z0-9.-]*hotcrp\.com(?:/[^\s\"'<>]*)?",
    re.IGNORECASE,
)
RELATED_SUBMISSION_LINK = re.compile(
    r"\b(?:call for papers|submission instructions|paper submission|"
    r"main conference paper submission|submit your work)\b",
    re.IGNORECASE,
)


class VisibleHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tokens: list[str] = []
        self.links: list[dict[str, str]] = []
        self._skip = 0
        self._href: str | None = None
        self._anchor: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript", "svg"}:
            self._skip += 1
        if tag == "a" and not self._skip:
            self._href = dict(attrs).get("href")
            self._anchor = []

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg"} and self._skip:
            self._skip -= 1
        if tag == "a" and self._href is not None:
            self.links.append({"text": " ".join(self._anchor), "href": self._href})
            self._href = None
            self._anchor = []

    def handle_data(self, data: str) -> None:
        if self._skip:
            return
        text = " ".join(data.split())
        if text:
            self.tokens.append(text)
            if self._href is not None:
                self._anchor.append(text)


def parse_html(raw: str, base_url: str) -> tuple[list[str], list[dict[str, str]]]:
    parser = VisibleHTMLParser()
    parser.feed(raw)
    links = [
        {"text": link["text"], "url": urljoin(base_url, link["href"])}
        for link in parser.links
        if link["href"] and not link["href"].startswith(("#", "mailto:", "javascript:"))
    ]
    return parser.tokens, links


def normalize_date(value: str) -> str | None:
    cleaned = re.sub(r"^(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+", "", value)
    cleaned = re.sub(r"(\d)(?:st|nd|rd|th)", r"\1", cleaned)
    cleaned = cleaned.replace(",", "")
    for fmt in ("%B %d %Y", "%d %B %Y"):
        try:
            return datetime.strptime(cleaned, fmt).date().isoformat()
        except ValueError:
            pass
    return None


def clean_label(text: str) -> str:
    label = DATE_PATTERN.sub("", text)
    label = re.sub(r"\s+", " ", label).strip(" :–—-|.")
    return label[:100] or "Paper submission"


def extract_deadlines(tokens: list[str], source_url: str, today: date) -> list[dict[str, object]]:
    found: dict[tuple[str, str], dict[str, object]] = {}
    for index, token in enumerate(tokens):
        if "artifact" in token.lower() or "camera" in token.lower():
            continue
        if not DEADLINE_TERMS.search(token):
            continue
        match = None
        for offset in (0, 1, -1, 2, -2):
            position = index + offset
            if 0 <= position < len(tokens):
                match = DATE_PATTERN.search(tokens[position])
                if match:
                    break
        if not match:
            continue
        iso_date = normalize_date(match.group(0))
        if not iso_date:
            continue
        label_match = DEADLINE_TERMS.search(token)
        label = clean_label(label_match.group(0) if label_match else token)
        deadline_date = date.fromisoformat(iso_date)
        key = (label.lower(), iso_date)
        found[key] = {
            "label": label[0].upper() + label[1:],
            "date": iso_date,
            "display_date": match.group(0),
            "days_remaining": (deadline_date - today).days,
            "status": "upcoming" if deadline_date >= today else "passed",
            "source_url": source_url,
        }
    return sorted(found.values(), key=lambda item: str(item["date"]))


def extract_nomination(
    tokens: list[str], links: list[dict[str, str]], source_url: str
) -> dict[str, str]:
    for link in links:
        candidate = f"{link['text']} {link['url']}"
        if NOMINATION_TERMS.search(candidate):
            return {
                "status": "found",
                "url": link["url"],
                "label": link["text"] or "TPC self-nomination information",
            }
    text = " ".join(tokens)
    match = NOMINATION_TERMS.search(text)
    if match:
        start = max(0, match.start() - 100)
        end = min(len(text), match.end() + 140)
        return {
            "status": "found",
            "url": source_url,
            "label": text[start:end].strip(),
        }
    return {
        "status": "not_found",
        "url": source_url,
        "label": "No TPC self-nomination information found on the monitored official page.",
    }


def related_tpc_urls(links: list[dict[str, str]], source_url: str) -> list[str]:
    source_host = urlparse(source_url).netloc
    urls: list[str] = []
    for link in links:
        candidate = f"{link['text']} {link['url']}"
        if not RELATED_TPC_LINK.search(candidate):
            continue
        parsed = urlparse(link["url"])
        if parsed.scheme not in {"http", "https"} or parsed.netloc != source_host:
            continue
        clean_url = parsed._replace(fragment="").geturl()
        if clean_url != source_url and clean_url not in urls:
            urls.append(clean_url)
    return urls[:3]


def extract_submission_sites(
    tokens: list[str], links: list[dict[str, str]]
) -> list[dict[str, str]]:
    sites: list[dict[str, str]] = []
    seen: set[str] = set()

    def add(url: str, label: str = "") -> None:
        clean_url = url.rstrip(".,);]") + ("/" if not url.rstrip(".,);]").endswith("/") else "")
        parsed = urlparse(clean_url)
        host = parsed.netloc.lower()
        if not host.endswith("hotcrp.com"):
            return
        clean_url = parsed._replace(scheme="https").geturl()
        short_host = host.removesuffix(".hotcrp.com")
        combined = f"{short_host} {label}".lower()
        if "artifact" in combined or re.search(r"(?:^|[-.\s])ae(?:[-.\s]|$)", combined):
            return
        if clean_url in seen:
            return
        seen.add(clean_url)
        clean_label = " ".join(label.split())
        if not clean_label or clean_label.startswith(("http://", "https://")):
            clean_label = short_host
        sites.append({"label": clean_label[:80], "url": clean_url})

    for link in links:
        add(link["url"], link["text"])
    for token in tokens:
        for match in HOTCRP_URL_PATTERN.finditer(token):
            add(match.group(0))
    return sites


def related_submission_urls(
    links: list[dict[str, str]], source_url: str
) -> list[str]:
    source_host = urlparse(source_url).netloc
    urls: list[str] = []
    for link in links:
        candidate = f"{link['text']} {link['url']}"
        parsed = urlparse(link["url"])
        if (
            RELATED_SUBMISSION_LINK.search(candidate)
            and parsed.scheme in {"http", "https"}
            and parsed.netloc == source_host
        ):
            clean_url = parsed._replace(fragment="").geturl()
            if clean_url != source_url and clean_url not in urls:
                urls.append(clean_url)
    return urls[:2]


def extract_aec_nomination(
    tokens: list[str], links: list[dict[str, str]], source_url: str
) -> dict[str, str]:
    text = " ".join(tokens)
    if not (AEC_ROLE_TERMS.search(text) and AEC_ACTION_TERMS.search(text)):
        return {
            "status": "not_found",
            "url": source_url,
            "label": "No AEC self-nomination information found on the monitored official page.",
        }

    application_url = ""
    for link in links:
        candidate = f"{link['text']} {link['url']}"
        if re.search(
            r"self[- ]nomination|nomination|apply|application|"
            r"forms\.gle|docs\.google\.com/forms",
            candidate,
            re.IGNORECASE,
        ):
            application_url = link["url"]
            break
    source_is_application_page = bool(
        re.search(
            r"(?:aec-call|for-reviewers|artifactcommittee)",
            urlparse(source_url).path,
            re.IGNORECASE,
        )
    )
    if not application_url and not source_is_application_page:
        return {
            "status": "not_found",
            "url": source_url,
            "label": "No AEC self-nomination information found on the monitored official page.",
        }
    return {
        "status": "found",
        "url": application_url or source_url,
        "label": "AEC self-nomination form",
    }


def fetch(url: str, timeout: int = 25, attempts: int = 2) -> tuple[str, str]:
    last_error: Exception | None = None
    for attempt in range(attempts):
        request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
        try:
            with urlopen(request, timeout=timeout) as response:
                content_type = response.headers.get("Content-Type", "")
                if "html" not in content_type:
                    raise ValueError(f"unexpected content type: {content_type}")
                charset = response.headers.get_content_charset() or "utf-8"
                return response.read(2_500_000).decode(charset, "replace"), response.geturl()
        except HTTPError:
            raise
        except (URLError, TimeoutError, ConnectionError, OSError) as error:
            last_error = error
            if attempt + 1 < attempts:
                time.sleep(1)
    assert last_error is not None
    raise last_error


def candidate_urls(conference: dict[str, object], today: date) -> list[str]:
    urls: list[str] = []
    for template in conference["urls"]:
        if "{year}" in template or "{yy}" in template:
            for year in (today.year + 1, today.year):
                urls.append(template.format(year=year, yy=str(year)[-2:]))
        elif template not in urls:
            urls.append(template)
    return urls


def infer_edition(url: str, tokens: list[str], today: date) -> str:
    url_years = re.findall(r"\b20\d{2}\b", url)
    valid = [int(year) for year in url_years if today.year - 1 <= int(year) <= today.year + 2]
    if valid:
        return str(max(valid))
    nearby_years = re.findall(r"\b20\d{2}\b", " ".join(tokens[:80]))
    valid = [int(year) for year in nearby_years if today.year - 1 <= int(year) <= today.year + 2]
    return str(max(valid)) if valid else "TBA"


def update_conference(
    conference: dict[str, object], today: date, previous: dict[str, object] | None
) -> dict[str, object]:
    errors: list[str] = []
    for url in candidate_urls(conference, today):
        try:
            raw, final_url = fetch(url)
            tokens, links = parse_html(raw, final_url)
            edition = infer_edition(final_url, tokens, today)
            previous_edition = str(previous.get("edition", "")) if previous else ""
            if (
                edition.isdigit()
                and previous_edition.isdigit()
                and int(edition) < int(previous_edition)
            ):
                errors.append(f"{final_url}: older edition {edition}")
                continue
            public_template = conference.get("public_url", final_url)
            public_url = public_template.format(year=edition, yy=edition[-2:])
            deadlines = extract_deadlines(tokens, public_url, today)
            submission_sites = extract_submission_sites(tokens, links)
            if not submission_sites:
                for submission_url in related_submission_urls(links, final_url):
                    try:
                        submission_raw, submission_final_url = fetch(
                            submission_url, timeout=10, attempts=1
                        )
                        submission_tokens, submission_links = parse_html(
                            submission_raw, submission_final_url
                        )
                        submission_sites.extend(
                            extract_submission_sites(
                                submission_tokens, submission_links
                            )
                        )
                    except (HTTPError, URLError, TimeoutError, ValueError, OSError):
                        continue
            submission_sites = list(
                {site["url"]: site for site in submission_sites}.values()
            )
            nomination = extract_nomination(tokens, links, public_url)
            checked_tpc_urls = [public_url]
            if nomination["status"] == "not_found":
                for related_url in related_tpc_urls(links, final_url):
                    try:
                        related_raw, related_final_url = fetch(
                            related_url, timeout=10, attempts=1
                        )
                        related_tokens, related_links = parse_html(
                            related_raw, related_final_url
                        )
                        checked_tpc_urls.append(related_final_url)
                        related_nomination = extract_nomination(
                            related_tokens, related_links, related_final_url
                        )
                        if related_nomination["status"] == "found":
                            nomination = related_nomination
                            break
                    except (HTTPError, URLError, TimeoutError, ValueError, OSError):
                        continue
            if nomination["status"] == "not_found" and edition.isdigit():
                for template in conference.get("tpc_urls", []):
                    tpc_url = template.format(year=edition, yy=edition[-2:])
                    try:
                        tpc_raw, tpc_final_url = fetch(
                            tpc_url, timeout=10, attempts=1
                        )
                        tpc_tokens, tpc_links = parse_html(tpc_raw, tpc_final_url)
                        checked_tpc_urls.append(tpc_final_url)
                        tpc_text = " ".join(tpc_tokens)
                        edition_matches = bool(
                            re.search(
                                rf"\b(?:CoNEXT\s+)?{re.escape(edition)}\b",
                                tpc_text,
                                re.IGNORECASE,
                            )
                        )
                        has_application = (
                            "shadow tpc" in tpc_text.lower()
                            and (
                                "how to apply" in tpc_text.lower()
                                or "application deadline" in tpc_text.lower()
                            )
                        )
                        if edition_matches and has_application:
                            public_template = conference.get(
                                "tpc_public_url", tpc_final_url
                            )
                            nomination = {
                                "status": "found",
                                "url": public_template.format(
                                    year=edition, yy=edition[-2:]
                                ),
                                "label": "Shadow TPC application",
                            }
                            break
                    except (HTTPError, URLError, TimeoutError, ValueError, OSError):
                        continue
            aec_nomination = extract_aec_nomination(tokens, links, public_url)
            checked_aec_urls = [public_url]
            if aec_nomination["status"] == "not_found" and edition.isdigit():
                for template in conference.get("aec_urls", []):
                    aec_url = template.format(year=edition, yy=edition[-2:])
                    try:
                        aec_raw, aec_final_url = fetch(
                            aec_url, timeout=10, attempts=1
                        )
                        aec_tokens, aec_links = parse_html(aec_raw, aec_final_url)
                        checked_aec_urls.append(aec_final_url)
                        aec_text = " ".join(aec_tokens)
                        edition_matches = bool(
                            re.search(
                                rf"\b[A-Za-z][A-Za-z-]*\s*[’']?"
                                rf"{re.escape(edition[-2:])}\b"
                                rf"|\b{re.escape(edition)}\b",
                                aec_text,
                                re.IGNORECASE,
                            )
                        )
                        candidate = extract_aec_nomination(
                            aec_tokens, aec_links, aec_final_url
                        )
                        if edition_matches and candidate["status"] == "found":
                            if (
                                candidate["url"] == aec_final_url
                                and conference.get("aec_public_url")
                            ):
                                candidate["url"] = conference["aec_public_url"].format(
                                    year=edition, yy=edition[-2:]
                                )
                            aec_nomination = candidate
                            break
                    except (HTTPError, URLError, TimeoutError, ValueError, OSError):
                        continue
            return {
                "id": conference["id"],
                "name": conference["name"],
                "area": conference["area"],
                "edition": edition,
                "source_url": public_url,
                "source_status": "ok",
                "deadlines": deadlines,
                "next_deadline": next(
                    (item for item in deadlines if item["status"] == "upcoming"), None
                ),
                "submission_sites": submission_sites,
                "tpc_nomination": nomination,
                "tpc_sources_checked": checked_tpc_urls,
                "aec_nomination": aec_nomination,
                "aec_sources_checked": checked_aec_urls,
            }
        except (HTTPError, URLError, TimeoutError, ValueError, OSError) as error:
            errors.append(f"{url}: {type(error).__name__}")

    if previous:
        retained = dict(previous)
        retained["source_status"] = "error"
        retained["source_error"] = "; ".join(errors)[:500]
        retained.setdefault("submission_sites", [])
        retained.setdefault(
            "aec_nomination",
            {
                "status": "unknown",
                "url": retained.get("source_url", ""),
                "label": "The official AEC source could not be checked.",
            },
        )
        retained.setdefault("aec_sources_checked", [])
        return retained

    return {
        "id": conference["id"],
        "name": conference["name"],
        "area": conference["area"],
        "edition": "TBA",
        "source_url": candidate_urls(conference, today)[-1],
        "source_status": "error",
        "source_error": "; ".join(errors)[:500],
        "deadlines": [],
        "next_deadline": None,
        "submission_sites": [],
        "tpc_nomination": {
            "status": "unknown",
            "url": candidate_urls(conference, today)[-1],
            "label": "The official source could not be checked.",
        },
        "tpc_sources_checked": [],
        "aec_nomination": {
            "status": "unknown",
            "url": candidate_urls(conference, today)[-1],
            "label": "The official AEC source could not be checked.",
        },
        "aec_sources_checked": [],
    }


def load_previous() -> dict[str, dict[str, object]]:
    if not OUTPUT.exists():
        return {}
    try:
        data = json.loads(OUTPUT.read_text(encoding="utf-8"))
        return {item["id"]: item for item in data.get("conferences", [])}
    except (json.JSONDecodeError, KeyError, TypeError):
        return {}


def build_payload(today: date) -> dict[str, object]:
    previous = load_previous()
    def update(item: dict[str, object]) -> dict[str, object]:
        return update_conference(item, today, previous.get(str(item["id"])))

    with ThreadPoolExecutor(max_workers=len(CONFERENCES)) as executor:
        conferences = list(executor.map(update, CONFERENCES))
    upcoming = sum(
        1
        for conference in conferences
        for deadline in conference["deadlines"]
        if deadline["status"] == "upcoming"
    )
    nominations = sum(
        1
        for conference in conferences
        if conference["tpc_nomination"]["status"] == "found"
    )
    aec_nominations = sum(
        1
        for conference in conferences
        if conference["aec_nomination"]["status"] == "found"
    )
    return {
        "last_checked": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "monitor_date": today.isoformat(),
        "summary": {
            "conferences": len(conferences),
            "upcoming_deadlines": upcoming,
            "tpc_nominations": nominations,
            "aec_nominations": aec_nominations,
        },
        "conferences": conferences,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Override monitor date (YYYY-MM-DD) for testing")
    parser.add_argument("--check", action="store_true", help="Validate without writing output")
    args = parser.parse_args()
    today = date.fromisoformat(args.date) if args.date else date.today()
    payload = build_payload(today)
    if not args.check:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    failures = [item["name"] for item in payload["conferences"] if item["source_status"] == "error"]
    print(
        f"Checked {len(payload['conferences'])} conferences; "
        f"{payload['summary']['upcoming_deadlines']} upcoming deadlines; "
        f"{payload['summary']['tpc_nominations']} TPC nomination pages; "
        f"{payload['summary']['aec_nominations']} AEC nomination pages."
    )
    if failures:
        print("Sources unavailable: " + ", ".join(failures), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
