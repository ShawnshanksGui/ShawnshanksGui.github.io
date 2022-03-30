---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
---


* **Incorporating intra-flow dependencies and inter-flow correlations for traffic matrix prediction.**    
Kaihui Gao, Dan Li, Li Chen, Jinkun Geng, **Fei Gui**, Yang Cheng, Yue Gu. 
IWQOS 2020

* **Predicting traffic demand matrix by considering inter-flow correlations.**

Kaihui Gao, Dan Li, Li Chen, Jinkun Geng, **Fei Gui**, Yang Cheng, Yue Gu.
INFOCOM workshop 2020

* **Sphinx: A Transport Protocol for High-Speed and Lossy Mobile Networks.**

Junfeng Li, Dan Li, Wenfei Wu, K.K. Ramakrishnan and Jinkun Geng, **Fei Gui**, Fanzhao Wang, Kai Zheng.
IPCCC 2019

* **Dante: Enabling fov-aware adaptive fec coding for 360-degree video streaming.**

Zhetao Li, **Fei Gui**, Jinkun Geng, Dan Li, Zhibo Wang, Junfeng Li, Yang Cheng, Usama Zafar.
APNet 2018


{% if author.googlescholar %}
  You can also find my articles on <u><a href="{{author.googlescholar}}">my Google Scholar profile</a>.</u>
{% endif %}

{% include base_path %}

{% for post in site.publications reversed %}
  {% include archive-single.html %}
{% endfor %}
