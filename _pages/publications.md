---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
---

* **RedTE: Real-time and Distributed Traffic Engineering for Burst Mitigation in Wide Area Networks.**    
**_Fei Gui_**, Songtao Wang, Dan Li, Li Chen, Kaihui Gao, Congcong Min, Yi Wang.
ACM SIGCOMM 2024, Sydney, Australia. **(Top #1 Conference in Computer Networks)**

* **Data-Driven Routing: A Typical Application of Digital Twin Network.**    
Zhiyu Wei, Songtao Wang, Dan Li, **_Fei Gui_**, Sihong Hong.   
International Conference on Digital Twins and Parallel Intelligence (DTPI) 2020.

* **Incorporating intra-flow dependencies and inter-flow correlations for traffic matrix prediction.**    
Kaihui Gao, Dan Li, Li Chen, Jinkun Geng, **_Fei Gui_**, Yang Cheng, Yue Gu. 
IWQOS 2020.

* **Predicting traffic demand matrix by considering inter-flow correlations.**
Kaihui Gao, Dan Li, Li Chen, Jinkun Geng, **_Fei Gui_**, Yang Cheng, Yue Gu.
INFOCOM workshop 2020.

* **Sphinx: A Transport Protocol for High-Speed and Lossy Mobile Networks.**
Junfeng Li, Dan Li, Wenfei Wu, K.K. Ramakrishnan and Jinkun Geng, **_Fei Gui_**, Fanzhao Wang, Kai Zheng.
IPCCC 2019. **(Best Paper Candidate)**

* **Dante: Enabling fov-aware adaptive fec coding for 360-degree video streaming.**
Zhetao Li, **_Fei Gui_**, Jinkun Geng, Dan Li, Zhibo Wang, Junfeng Li, Yang Cheng, Usama Zafar.
APNet 2018.


{% if author.googlescholar %}
  You can also find my articles on <u><a href="{{author.googlescholar}}">my Google Scholar profile</a>.</u>
{% endif %}

{% include base_path %}

{% for post in site.publications reversed %}
  {% include archive-single.html %}
{% endfor %}
