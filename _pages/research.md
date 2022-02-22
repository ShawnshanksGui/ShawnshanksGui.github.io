---
layout: archive
title: "Research"
permalink: /research/
author_profile: true
---
## How to do first-class research 
[You and Your research, Dr. Richard W. Hamming](https://www.cs.virginia.edu/~robins/YouAndYourResearch.pdf)
[The craft of research, WAYNE C. BOOTH, GREGORY G. COLOMB, JOSEPH M. WILLIAMS](http://course.sdu.edu.cn/G2S/eWebEditor/uploadfile/20140306165625006.pdf)


{% if author.googlescholar %}
  You can also find my articles on <u><a href="{{author.googlescholar}}">my Google Scholar profile</a>.</u>
{% endif %}

{% include base_path %}

{% for post in site.research reversed %}
  {% include archive-single.html %}
{% endfor %}
