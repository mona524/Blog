#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Mona on 2017/9/14



comment_list=[
    {"id":1,"content":"...","Pid":None},
    {"id":2,"content":"...","Pid":None},
    {"id":3,"content":"...","Pid":None},
    {"id":4,"content":"...","Pid":1},
    {"id":5,"content":"...","Pid":1},
    {"id":6,"content":"...","Pid":4},
    {"id":7,"content":"...","Pid":3},
    {"id":8,"content":"...","Pid":7},
    {"id":9,"content":"...","Pid":None},
]


for i in comment_list:
    i['chirden_comment'] = []

