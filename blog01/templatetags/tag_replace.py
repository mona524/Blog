#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Mona on 2017/9/9

from django import template

register = template.Library()

def myreplace(value,arg):
    return value.replace(arg,'&nbsp;')

register.filter('myreplace', myreplace)
