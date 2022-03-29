---
layout: archive
title: ""
permalink: /research/
author_profile: true
---

# Why research
  [许知远对话傅高义, 十三邀](https://movie.douban.com/subject/35173861/episode/11/) by Ezra Vogel and Zhiyuan Xu

  [学术作为一种志业](https://book.douban.com/subject/30309618/) by Max Weber

<br/>

# How to do first-class research 
  [You and Your research](https://www.cs.virginia.edu/~robins/YouAndYourResearch.pdf) by Richard W. Hamming

  [The craft of research](http://course.sdu.edu.cn/G2S/eWebEditor/uploadfile/20140306165625006.pdf) by Wayne C. Booth 

  [Research in spare time](https://yuandong-tian.com/research_in_spare_time.pdf) by Yuandong Tian

<br/>

# How to write paper


{% if author.googlescholar %}
  You can also find my articles on <u><a href="{{author.googlescholar}}">my Google Scholar profile</a>.</u>
{% endif %}

{% include base_path %}

{% for post in site.research reversed %}
  {% include archive-single.html %}
{% endfor %}
