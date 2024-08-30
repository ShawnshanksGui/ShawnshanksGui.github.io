---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
---

* **RedTE: Mitigating Subsecond Traffic Bursts with Real-time and Distributed Traffic Engineering.**    
**_Fei Gui_**, Songtao Wang, Dan Li, Li Chen, Kaihui Gao, Congcong Min, Yi Wang.   
[ACM SIGCOMM 2024](https://conferences.sigcomm.org/sigcomm/2024/). **(Top #1 Conference in Computer Networks)**    

* **Incorporating intra-flow dependencies and inter-flow correlations for traffic matrix prediction.**    
Kaihui Gao, Dan Li, Li Chen, Jinkun Geng, **_Fei Gui_**, Yang Cheng, Yue Gu.   
ACM IWQOS 2020.  

* **Predicting traffic demand matrix by considering inter-flow correlations.**   
Kaihui Gao, Dan Li, Li Chen, Jinkun Geng, **_Fei Gui_**, Yang Cheng, Yue Gu.   
IEEE INFOCOM workshop 2020.  


* **Sphinx: A Transport Protocol for High-Speed and Lossy Mobile Networks.**    
Junfeng Li, Dan Li, Wenfei Wu, K.K. Ramakrishnan and Jinkun Geng, **_Fei Gui_**, Fanzhao Wang, Kai Zheng.   
IEEE IPCCC 2019. **(Best Paper Candidate)**   

* **Dante: Enabling fov-aware adaptive fec coding for 360-degree video streaming.**   
Zhetao Li, **_Fei Gui_**, Jinkun Geng, Dan Li, Zhibo Wang, Junfeng Li, Yang Cheng, Usama Zafar.  
ACM APNet 2018.   


{% if author.googlescholar %}
  You can also find my articles on <u><a href="{{author.googlescholar}}">my Google Scholar profile</a>.</u>
{% endif %}

{% include base_path %}

{% for post in site.publications reversed %}
  {% include archive-single.html %}
{% endfor %}
