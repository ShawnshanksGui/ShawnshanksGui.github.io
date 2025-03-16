---
layout: archive
title: ""
permalink: /publications/
author_profile: true
---


* [**NSDI'25**] Accelerating Design Space Exploration for LLM Training Systems with Multi-experiment Parallel Simulation.    
<u>Fei Gui</u>, Kaihui Gao, Li Chen, Dan Li, Vincent Liu, Ran Zhang, Hongbing Yang, Dian Xiong.

* [**SIGCOMM'24**] RedTE: Mitigating Subsecond Traffic Bursts with Real-time and Distributed Traffic Engineering.    
<u>Fei Gui</u>, Songtao Wang, Dan Li, Li Chen, Kaihui Gao, Congcong Min, Yi Wang.   
<!-- **ACM SIGCOMM 2024. (Top Conference in Computer Networks)**     -->

* [**IWQoS'20**] Incorporating intra-flow dependencies and inter-flow correlations for traffic matrix prediction.   
Kaihui Gao, Dan Li, Li Chen, Jinkun Geng, <u>Fei Gui</u>, Yang Cheng, Yue Gu.   

* [**INFOCOM workshop'20**] Predicting traffic demand matrix by considering inter-flow correlations.   
Kaihui Gao, Dan Li, Li Chen, Jinkun Geng, <u>Fei Gui</u>, Yang Cheng, Yue Gu.    


* [**IPCCC'19**] Sphinx: A Transport Protocol for High-Speed and Lossy Mobile Networks.    
Junfeng Li, Dan Li, Wenfei Wu, K.K. Ramakrishnan and Jinkun Geng, <u>Fei Gui</u>, Fanzhao Wang, Kai Zheng.   
**(Best Paper Candidate)**   

* [**APNet'18**] Dante: Enabling fov-aware adaptive fec coding for 360-degree video streaming.   
Zhetao Li, <u>Fei Gui</u>, Jinkun Geng, Dan Li, Zhibo Wang, Junfeng Li, Yang Cheng, Usama Zafar.  
<!-- **ACM APNet 2018. (CCF C)**   -->


{% if author.googlescholar %}
  You can also find my articles on <u><a href="{{author.googlescholar}}">my Google Scholar profile</a>.</u>
{% endif %}

{% include base_path %}

{% for post in site.publications reversed %}
  {% include archive-single.html %}
{% endfor %}
