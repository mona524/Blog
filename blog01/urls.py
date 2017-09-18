#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Mona on 2017/9/5

from django.conf.urls import url
from blog01 import views

urlpatterns = [
    url(r'^article/delete', views.delete),
    url(r'(?P<username>\w+)/articles/(?P<condition>\w+)/(?P<para>\d+-\d+|\w+)', views.user),
    url(r'(?P<username>\w+)/articles_index/(?P<article_id>\d+)', views.articles_index),
    url(r'(?P<username>\w+)/upload_file', views.upload_file),
    url(r'(?P<username>\w+)/add_category_tag', views.add_category_tag),
    url(r'(?P<username>\w+)/add_article', views.add_article),
    url(r'(?P<username>\w+)/articles/(?P<article_id>\d+)', views.articles),
    url(r'^article_up', views.article_up),
    url(r'^article_comment', views.article_comment),
    url(r'user_manager', views.user_manager),
    url(r'(?P<username>.*)', views.user),

]
