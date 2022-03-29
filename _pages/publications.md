---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
---


Incorporating intra-flow dependencies and inter-flow correlations for traffic matrix prediction. K Gao, D Li, L Chen, J Geng, F Gui, Y Cheng, Y Gu. IWQOS 2020.

Dante: Enabling fov-aware adaptive fec coding for 360-degree video streaming. Z Li, F Gui, J Geng, D Li, Z Wang, J Li, Y Cheng, U Zafar.  APNet 2018.


{% if author.googlescholar %}
  You can also find my articles on <u><a href="{{author.googlescholar}}">my Google Scholar profile</a>.</u>
{% endif %}

{% include base_path %}

{% for post in site.publications reversed %}
  {% include archive-single.html %}
{% endfor %}
