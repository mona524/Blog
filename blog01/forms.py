#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Mona on 2017/9/6

from django import forms
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from blog01 import models

# ******************************register html*********************************************************
class RegisterForm(forms.Form):
    '''create a Form class for register html'''

    def __init__(self, request=None,*args,**kwargs):
        super(RegisterForm,self).__init__(*args,**kwargs)
        self.request=request #要往session里加值，必须重写init方法，将request传入


    username = forms.CharField(min_length=5, #设置字段最小长度为5
                               max_length=12,
                               widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Username'}),
                               error_messages=({'required':'不能为空'})) #设置默认错误信息

    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}),
                               error_messages={'required':'不能为空'})
    re_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}),
                                  error_messages={'required': '不能为空'})
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Email'}),
                             error_messages={'required': '不能为空','invalid':'格式错误'})

    valid_code = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Valid Code'}),
                                 error_messages={'required': '不能为空', 'invalid': '格式错误'})

    def clean_password(self):
        '''tail a hook for verification  设置局部的钩子对form表单定制验证方法，格式参照源码 '''
        if len(self.cleaned_data['password'])>=8:

            return self.cleaned_data['password']
        else:
            raise ValidationError('密码长度必须大于8位')

    def clean_re_password(self):
        '''tail a function for verification  '''
        if len(self.cleaned_data['re_password']) >= 8:
            return self.cleaned_data['re_password']
        else:
            raise ValidationError('密码长度必须大于8位')

    def clean_username(self):
        '''tail a function for username verification'''
        if self.cleaned_data['username'].isdigit() or self.cleaned_data['username'].isalpha():
            raise ValidationError('用户名必须由数字和字母组成')
        else:
            if models.UserInfo.objects.filter(username=self.cleaned_data['username']):
                raise ValidationError('用户名已占用，请更改用户名')
            else:
                return self.cleaned_data['username']

    def clean_valid_code(self):
        '''set global handler for valid code verification'''
        if self.cleaned_data.get('valid_code', '0').upper() == self.request.session['validCode'].upper():
            return self.cleaned_data['valid_code']
        else:
            raise ValidationError('验证码错误')

    def clean(self):
        '''set global hook for password verification. if first password equal repeat password,
        设置全局对钩子，对多个字段同时比较或验证'''
        if self.cleaned_data.get("password",0) == self.cleaned_data.get("re_password",1):
            return self.cleaned_data
        else:
            raise ValidationError("密码不一致")


# ****************************************************************************************************