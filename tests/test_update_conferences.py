import importlib.util
import unittest
from datetime import date
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "update_conferences.py"
SPEC = importlib.util.spec_from_file_location("update_conferences", MODULE_PATH)
monitor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(monitor)


class ConferenceMonitorTests(unittest.TestCase):
    def test_monitored_conferences_include_conext_not_infocom(self):
        ids = [conference["id"] for conference in monitor.CONFERENCES]
        self.assertIn("conext", ids)
        self.assertNotIn("infocom", ids)

    def test_parse_html_ignores_scripts_and_resolves_links(self):
        tokens, links = monitor.parse_html(
            """
            <style>fake deadline</style>
            <p>Full paper submission: December 8, 2026</p>
            <a href="/tpc-nomination">TPC self-nomination form</a>
            """,
            "https://example.org/cfp/",
        )
        self.assertNotIn("fake deadline", tokens)
        self.assertEqual(links[0]["url"], "https://example.org/tpc-nomination")

    def test_extract_deadlines_normalizes_and_marks_status(self):
        deadlines = monitor.extract_deadlines(
            [
                "Important Dates",
                "Abstract registrations due:",
                "Tuesday, December 1, 2026, 5:59 pm EST",
                "Complete paper submissions due:",
                "8 December 2026",
            ],
            "https://example.org/cfp",
            date(2026, 10, 24),
        )
        self.assertEqual([item["date"] for item in deadlines], ["2026-12-01", "2026-12-08"])
        self.assertTrue(all(item["status"] == "upcoming" for item in deadlines))

    def test_nomination_requires_explicit_nomination_language(self):
        ordinary = monitor.extract_nomination(
            ["Program Committee", "Alice", "Bob"], [], "https://example.org"
        )
        explicit = monitor.extract_nomination(
            [],
            [{"text": "TPC self-nomination form", "url": "https://example.org/form"}],
            "https://example.org",
        )
        self.assertEqual(ordinary["status"], "not_found")
        self.assertEqual(explicit["status"], "found")
        self.assertEqual(explicit["url"], "https://example.org/form")

    def test_shadow_tpc_call_is_treated_as_an_application(self):
        result = monitor.extract_nomination(
            ["Call For Shadow TPC Members"],
            [],
            "https://example.org/shadow",
        )
        self.assertEqual(result["status"], "found")

    def test_extract_submission_sites_excludes_artifact_hotcrp(self):
        sites = monitor.extract_submission_sites(
            [],
            [
                {
                    "text": "Fall submission",
                    "url": "https://conf27-fall.hotcrp.com/",
                },
                {
                    "text": "Artifact submission",
                    "url": "https://conf27-ae.hotcrp.com/",
                },
                {
                    "text": "HotCRP AE Submission Site",
                    "url": "https://conf27ae.hotcrp.com/",
                },
            ],
        )
        self.assertEqual(
            sites,
            [
                {
                    "label": "Fall submission",
                    "url": "https://conf27-fall.hotcrp.com/",
                }
            ],
        )

    def test_extract_aec_nomination_requires_role_and_application(self):
        found = monitor.extract_aec_nomination(
            [
                "Interested in Reviewing Artifacts?",
                "Join the Artifact Evaluation Committee",
                "Apply now",
            ],
            [
                {
                    "text": "self-nomination form",
                    "url": "https://forms.gle/example",
                }
            ],
            "https://example.org/aec",
        )
        authors_only = monitor.extract_aec_nomination(
            ["Artifact submission instructions", "The AEC will review artifacts"],
            [],
            "https://example.org/artifacts",
        )
        self.assertEqual(found["status"], "found")
        self.assertEqual(found["url"], "https://forms.gle/example")
        self.assertEqual(authors_only["status"], "not_found")

    def test_aec_navigation_without_application_form_is_not_found(self):
        result = monitor.extract_aec_nomination(
            ["Artifact Evaluation Committee", "Call for Evaluators"],
            [{"text": "Committee", "url": "https://example.org/aec-committee"}],
            "https://example.org/cfp",
        )
        self.assertEqual(result["status"], "not_found")

    def test_related_tpc_urls_stay_on_official_host(self):
        links = [
            {"text": "Program Committee", "url": "https://conf.example.org/committee/"},
            {"text": "TPC form", "url": "https://forms.example.com/tpc"},
            {"text": "Call for Papers", "url": "https://conf.example.org/cfp/"},
        ]
        self.assertEqual(
            monitor.related_tpc_urls(links, "https://conf.example.org/cfp/"),
            ["https://conf.example.org/committee/"],
        )

    def test_candidate_urls_prioritize_next_edition(self):
        conference = {
            "urls": [
                "https://example.org/{year}/cfp",
                "https://example.org/archive",
            ]
        }
        self.assertEqual(
            monitor.candidate_urls(conference, date(2026, 10, 24)),
            [
                "https://example.org/2027/cfp",
                "https://example.org/2026/cfp",
                "https://example.org/archive",
            ],
        )

    def test_infer_edition_prefers_official_url_year(self):
        edition = monitor.infer_edition(
            "https://example.org/conference/2027/cfp",
            ["Publication in the March 2028 journal issue"],
            date(2026, 10, 24),
        )
        self.assertEqual(edition, "2027")


if __name__ == "__main__":
    unittest.main()
