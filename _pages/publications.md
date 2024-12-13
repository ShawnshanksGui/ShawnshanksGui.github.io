---
layout: archive
title: ""
permalink: /publications/
author_profile: true
---


* RedTE: Mitigating Subsecond Traffic Bursts with Real-time and Distributed Traffic Engineering.    
<u>Fei Gui</u>, Songtao Wang, Dan Li, Li Chen, Kaihui Gao, Congcong Min, Yi Wang.   
**ACM SIGCOMM 2024. (Top Conference in Computer Networks)**    

* Incorporating intra-flow dependencies and inter-flow correlations for traffic matrix prediction.   
Kaihui Gao, Dan Li, Li Chen, Jinkun Geng, <u>Fei Gui</u>, Yang Cheng, Yue Gu.   
**ACM IWQOS 2020. (CCF B)**  

* Predicting traffic demand matrix by considering inter-flow correlations.   
Kaihui Gao, Dan Li, Li Chen, Jinkun Geng, <u>Fei Gui<u>, Yang Cheng, Yue Gu.    
**IEEE INFOCOM workshop 2020.**   

* Sphinx: A Transport Protocol for High-Speed and Lossy Mobile Networks.    
Junfeng Li, Dan Li, Wenfei Wu, K.K. Ramakrishnan and Jinkun Geng, <u>Fei Gui</u>, Fanzhao Wang, Kai Zheng.   
**IEEE IPCCC 2019. (CCF C, Best Paper Candidate)**   

* Dante: Enabling fov-aware adaptive fec coding for 360-degree video streaming.   
Zhetao Li, <u>Fei Gui</u>, Jinkun Geng, Dan Li, Zhibo Wang, Junfeng Li, Yang Cheng, Usama Zafar.  
**ACM APNet 2018. (CCF C)**  


{% if author.googlescholar %}
  You can also find my articles on <u><a href="{{author.googlescholar}}">my Google Scholar profile</a>.</u>
{% endif %}

{% include base_path %}

{% for post in site.publications reversed %}
  {% include archive-single.html %}
{% endfor %}
