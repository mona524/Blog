from django.shortcuts import render,redirect,HttpResponse
from django.contrib import auth
from blog01.models import *
from django.contrib.auth.decorators import login_required
from blog01 import models
from PIL import Image,ImageDraw,ImageFont
import random
from io import BytesIO
import json
from Blog.settings import FUNCTION
from django.core.paginator import Paginator
from blog01 import forms
from django.db.models import Avg, Sum, Min, Max, Count,F,Q
import calendar
import os
import collections

# Create your views here.

def func(request):
    return {'func':FUNCTION}

def index(request,**kwargs):
    '''index function, get data and render index html'''
    user = request.user
    type_choices = models.Article.type_choices
    current_type_choices_id = int(kwargs.get("article_type_id",0))

    article_list = models.Article.objects.all()

    # article = Article.objects.all()
    page = Paginator(article_list, 8)

    if request.GET.get('page'):
        page_num = request.GET.get('page')
        articles = page.page(page_num)
    else:
        articles = page.page(1)

    return render(request,'index.html',{'user':user,
                                        'type_choices':type_choices,
                                        'current_type_choices_id':current_type_choices_id,
                                        'article_list':article_list,'articles':articles})

def log_in(request):
    '''render login html,get form info and if valid code and user ,return true and login user;
    else return false and error message'''

    article_id = request.GET.get('article_id')
    if request.method == "POST":


        error_message=''
        state = False
        valid_code = request.POST.get('valid_code')
        validCode = request.session['validCode']

        if validCode.upper() == valid_code.upper():
            username = request.POST.get('username')
            password = request.POST.get('password')
            usr_obj= auth.authenticate(username=username,password=password)
            if usr_obj:
                state = True
                auth.login(request,usr_obj)
            else:
                error_message='用户名或密码错误'
        else:
            error_message='验证码错误'


        data = {'state':state,'error_message':error_message,'article_id ':article_id }

        return HttpResponse(json.dumps(data))

    return render(request,'login.html')

def register(request):
    '''render register html'''

    form_obj = forms.RegisterForm()
    if request.method == "POST":
        reponse_data = {}
        state = False
        error_message = ''
        form_obj = forms.RegisterForm(request,request.POST)#

        if form_obj.is_valid(): #验证form 表单里的数据是否合格
            data = form_obj.cleaned_data  #clean_data取出jango form表单里的合格数据
            data.pop('re_password')  #删除非数据库里的字段
            data.pop('valid_code')
            file_obj = request.FILES.get("avatar")
            data['avatar'] = file_obj
            UserInfo.objects.create_user(**data) #userinfo继承django user，并创建用户（创建用户存数据时会自动给用户密码加密）
            state=True

        else:
            errors = form_obj.errors
            error_message = errors
        reponse_data['error_message']=error_message
        reponse_data['state']=state
        return HttpResponse(json.dumps(reponse_data)) #pythons数据类型和js数据类型不一样，记得json序列化一下

    return render(request,'register.html',{'form_obj':form_obj})

def valid_code(request):
    '''create valid code picture'''
    f = BytesIO() #实例化BytesIo,创建一个内存存储文件的句柄
    img = Image.new(mode='RGB', #图片格式
                    size=(120,30), #图片大小
                    color=(random.randint(0,255),random.randint(0,255),random.randint(0,255))) #随机设置图片颜色
    draw = ImageDraw.Draw(img,mode="RGB")  #创建画笔句柄，讲imag 传入进去

    code_list=[] #存储验证码
    for i in range(5):
        char = random.choice([chr(random.randint(65,90)),str(random.randint(0,9))]) #随机生成字母和数字
        code_list.append(char) #添加到存储验证码到列表
        font = ImageFont.truetype('blog01/static/bootstrap/fonts/kumo.ttf',28)  #设置字体和大小
        draw.text([i*24,0],char,(random.randint(0,255),random.randint(0,255),random.randint(0,255)),font=font)

    #画干扰线
    for i in range(5):
        x1 = random.randint(0, 120)
        y1 = random.randint(0, 120)
        x2 = random.randint(0, 120)
        y2 = random.randint(0, 120)
        draw.line((x1, y1, x2, y2), fill=(random.randint(0, 255),random.randint(10, 255),random.randint(64, 255)))

    # 画干扰点
    for i in range(40):
        draw.point([random.randint(0, 120), random.randint(0, 30)], fill=(random.randint(0, 255),random.randint(10, 255),random.randint(64, 255)))

    # 画干扰圆
    for i in range(40):
        draw.point([random.randint(0,120), random.randint(0, 30)], fill=(random.randint(0, 255),random.randint(10, 255),random.randint(64, 255)))
        x = random.randint(0, 120)
        y = random.randint(0, 30)
        draw.arc((x, y, x + 4, y + 4), 0, 90, fill=(random.randint(0, 255),random.randint(10, 255),random.randint(64, 255)))

    img.save(f,'png') #讲绘制好的图片保存到f内存里
    data = f.getvalue() #从f里获取存取的二进制文件

    validCode = ''.join(code_list)  #拼接验证码

    request.session['validCode']=validCode #讲验证码存入session里

    return HttpResponse(data) #讲二进制文件返回给前端

@login_required
def log_out(request):
    '''logout function'''
    auth.logout(request)
    return redirect('/index/')

@login_required
def set_password(request):
    return render(request,'setpassword.html')

def user(request,username,**kwargs):

    if UserInfo.objects.filter(username=username):

        user_obj = UserInfo.objects.filter(username=username)[0]
        current_blog = Blog.objects.filter(user=user_obj).first()

        #园龄
        user_entry_time = UserInfo.objects.archive(username=user_obj.username)

        #粉丝数：
        fan = UserFans.objects.filter(user=user_obj).values('follower').aggregate(Count('nid'))

        fan_count = fan['nid__count']

        #日历
        now_time = time.localtime(time.time())
        now_calendar = calendar.month(now_time[0],now_time[1])
        now_calendar1=now_calendar

        #查询每个分类下的文章数
        category_count_list = Article.objects.filter(blog=current_blog).values_list('category__title','category__nid').annotate(Count('nid'))

        #查询每个标签下的文章数
        tag_count_list = Article.objects.filter(blog=current_blog).values_list('tags__title','tags__nid').annotate(Count('nid'))

        #查询时间分类下的文章数
        date = Article.objects.archive(blog=current_blog)
        date_list =set(date)

        data_count_list = []
        for i in date_list:
            date_count = (i ,date.count(i))
            data_count_list.append(date_count)

        article_list = Article.objects.filter(blog__user=user_obj)

        if kwargs.get("condition") :
            con = kwargs.get("condition")
            if con == "category":
                article_list = Article.objects.filter(blog__user=user_obj,category_id=kwargs.get("para"))
            elif con == 'tags':
                article_list = Article.objects.filter(blog__user=user_obj,tags__nid=kwargs.get('para'))
            elif con == 'date':
                article_list = Article.objects.filter(blog__user=user_obj,create_time__startswith = kwargs.get('para'))

        return render(request,'user.html',{'user':user_obj,
                                           'article_list':article_list,
                                           'category_count_list':category_count_list,
                                           'tag_count_list':tag_count_list,
                                           'data_count_list':data_count_list,
                                           'user_entry_time':user_entry_time,
                                           'fan_count':fan_count,
                                           'request':request

                                           })
    else:
        return HttpResponse('404:page not found1111')

def articles(request,username,article_id):

    if Article.objects.filter(nid=article_id):
        article_object = Article.objects.filter(nid=article_id).first()
        user_obj = article_object.blog.user
        current_blog = Blog.objects.filter(user=user_obj).first()

        # 园龄
        user_entry_time = UserInfo.objects.archive(username=user_obj.username)

        # 粉丝数：
        fan = UserFans.objects.filter(user=user_obj).values('follower').aggregate(Count('nid'))
        fan_count = fan['nid__count']

        # 查询每个分类下的文章数
        category_count_list = Article.objects.filter(blog=current_blog).values_list('category__title','category__nid').annotate(
            Count('nid'))

        # 查询每个标签下的文章数
        tag_count_list = Article.objects.filter(blog=current_blog).values_list('tags__title','tags__nid').annotate(Count('nid'))

        # 查询时间分类下的文章数
        date = Article.objects.archive(blog=current_blog)
        date_list = set(date)

        data_count_list = []
        for i in date_list:
            date_count = (i, date.count(i))
            data_count_list.append(date_count)

        content = ArticleDetail.objects.get(article_id=article_id).content
        content = content.split('\n')

        #查询评论
        comment_list = Comment.objects.filter(article=article_object)

        return render(request,'user_article.html',{'article_content':content,
                                                   'user': user_obj,
                                                   'article':article_object,
                                                   'category_count_list': category_count_list,
                                                   'tag_count_list': tag_count_list,
                                                   'data_count_list': data_count_list,
                                                   'user_entry_time': user_entry_time,
                                                   'fan_count': fan_count,
                                                   'request':request,
                                                   'comment_list':comment_list
                                                   })

    else:
        return HttpResponse('404:page not found')

def article_up(request):
    '''article poll up'''
    response_data = {'state':False}
    article_id = request.POST.get('article_id')
    user_id = request.user.nid

    if ArticleUpDown.objects.filter(article_id=article_id,user_id=user_id):
        response_data['state'] = True
    else:
        ArticleUpDown.objects.create(article_id=article_id,user_id=user_id)
        Article.objects.filter(nid=article_id).update(up_count = F('up_count')+1)

    return HttpResponse(json.dumps(response_data))

@login_required
def article_comment(request):
    article_id = request.POST.get('article_id')
    user_id = request.user.nid
    comment_content = request.POST.get('content')
    if request.POST.get('parent_comment_id'):
        parent_comment_id = request.POST.get('parent_comment_id')
        comment_object = Comment.objects.create(article_id=article_id,user_id=user_id,content=comment_content,parent_id_id=parent_comment_id)

    else:
        comment_object = Comment.objects.create(article_id=article_id,user_id=user_id,content=comment_content)

    Article.objects.filter(nid=article_id).update(comment_count= F('comment_count')+1)
    count = Article.objects.filter(nid=article_id).first().comment_count

    return render(request,'add_comment.html',{'comment_object':comment_object,
                                              'count':count,
                                              'request':request
                                              })

@login_required
def user_manager(request):
    username = request.user
    if UserInfo.objects.filter(username=username):
        user_obj = UserInfo.objects.filter(username=username).first()

        article_list = Article.objects.filter(blog__user=user_obj)

        return render(request,'user_manage.html',
                      {'user':user_obj,
                       'article_list':article_list})

@login_required
def add_article(request,username):
    '''add an article'''
    user_obj = UserInfo.objects.filter(username=username).first()
    category_list = Category.objects.filter(blog__user=user_obj)
    tag_list = Tag.objects.filter(blog__user=user_obj)

    type_list = Article.type_choices
    if request.method == 'POST':
        blog = Blog.objects.filter(user=user_obj).first()
        title = request.POST.get('title')
        desc = request.POST.get('desc')
        content = request.POST.get('content')
        category = request.POST.getlist('category')[0]
        tag_list = request.POST.getlist('tag')
        type_id = request.POST.getlist('type')[0]

        category_obj = Category.objects.filter(title=category).first()
        article = Article.objects.create(title=title,desc=desc,category=category_obj,blog=blog,article_type_id=type_id)
        ArticleDetail.objects.create(article=article,content=content)

        for i in tag_list:
            tag = Tag.objects.filter(title=i).first()
            Article2Tag.objects.create(article=article,tag=tag)

        nid = str(article.nid)

        return redirect('/blog/'+username+'/articles/'+nid)


    return render(request,'add_article.html',{'user_obj':user_obj,
                                             'category_list':category_list,
                                              'tag_list':tag_list,
                                              'type_list':type_list })

@login_required
def upload_file(request,username):
    '''deal with file which uploaded when add an article'''
    path = "blog01/media/upload/user" + username
    if not os.path.exists(path):
        os.mkdir(path)

    file_obj=request.FILES.get("imgFile")
    filename=file_obj.name
    with open(path+'/'+filename,"wb") as f:
        for chunk in file_obj.chunks():
            f.write(chunk)

    response_put={
        "error":0,
        "url":"/media/upload/user"+username+'/'+filename
    }


    return HttpResponse(json.dumps(response_put))

@login_required
def add_category_tag(request,username):
    '''add category or tag'''
    user_obj = UserInfo.objects.filter(username=username).first()
    response_data={}
    if request.POST.get('category'):
        category = request.POST.get('category')
        blog = Blog.objects.filter(user=user_obj).first()
        Category.objects.create(title=category,blog=blog)
        response_data['category']=category

    else:
        tag = request.POST.get('tag')
        blog = Blog.objects.filter(user=user_obj).first()
        Tag.objects.create(title=tag, blog=blog)
        response_data['tag'] = tag

    return HttpResponse(json.dumps(response_data))

@login_required
def delete(request):
    '''delete an article and related comment'''
    article_id = request.POST.get('article_id')
    article = Article.objects.filter(nid=article_id).first()

    comment_list = Comment.objects.filter(article=article)
    for comment in comment_list:
        comment.delete()
    article.delete()

    return HttpResponse(1)

def articles_index(request,username,article_id):

    if request.is_ajax():
        comment_list = Comment.objects.filter(article_id=article_id).values('nid','content','parent_id_id','create_time','user')
        # print(comment_list)
        comment_dict = collections.OrderedDict()
        for comment in comment_list:

            comment['children_comments'] = []
            user_id = comment['user']
            user_name = UserInfo.objects.get(nid=user_id)
            comment['user']=user_name.username
            comment['create_time'] = comment['create_time'].strftime('%Y-%m-%d %H:%M')

            comment_dict[comment['nid']]=comment

        ret = []
        for comment in comment_dict:
            if comment_dict[comment]['parent_id_id']:
                pid = comment_dict[comment]['parent_id_id']
                comment_dict[pid]['children_comments'].append(comment_dict[comment])

            else:
                ret.append(comment_dict[comment])

        return HttpResponse(json.dumps(ret))

    if Article.objects.filter(nid=article_id):
        article_object = Article.objects.filter(nid=article_id).first()
        user_obj = article_object.blog.user
        current_blog = Blog.objects.filter(user=user_obj).first()

        # 园龄
        user_entry_time = UserInfo.objects.archive(username=user_obj.username)

        # 粉丝数：
        fan = UserFans.objects.filter(user=user_obj).values('follower').aggregate(Count('nid'))
        fan_count = fan['nid__count']

        # 查询每个分类下的文章数
        category_count_list = Article.objects.filter(blog=current_blog).values_list('category__title','category__nid').annotate(
            Count('nid'))

        # 查询每个标签下的文章数
        tag_count_list = Article.objects.filter(blog=current_blog).values_list('tags__title','tags__nid').annotate(Count('nid'))

        # 查询时间分类下的文章数
        date = Article.objects.archive(blog=current_blog)
        date_list = set(date)

        data_count_list = []
        for i in date_list:
            date_count = (i, date.count(i))
            data_count_list.append(date_count)

        content = ArticleDetail.objects.get(article_id=article_id).content
        content = content.split('\n')

        #查询评论
        comment_list = Comment.objects.filter(article=article_object)

        return render(request,'user_article_index.html',{'article_content':content,
                                                   'user': user_obj,
                                                   'article':article_object,
                                                   'category_count_list': category_count_list,
                                                   'tag_count_list': tag_count_list,
                                                   'data_count_list': data_count_list,
                                                   'user_entry_time': user_entry_time,
                                                   'fan_count': fan_count,
                                                   'request':request,
                                                   'comment_list':comment_list
                                                   })

    else:
        return HttpResponse('404:page not found')


@login_required
def article_index_comment(request):
    article_id = request.POST.get('article_id')
    user_id = request.user.nid
    comment_content = request.POST.get('content')
    if request.POST.get('parent_comment_id'):
        parent_comment_id = request.POST.get('parent_comment_id')
        comment_object = Comment.objects.create(article_id=article_id,user_id=user_id,content=comment_content,parent_id_id=parent_comment_id)

    else:
        comment_object = Comment.objects.create(article_id=article_id,user_id=user_id,content=comment_content)

    Article.objects.filter(nid=article_id).update(comment_count= F('comment_count')+1)
    count = Article.objects.filter(nid=article_id).first().comment_count

    comment_id = comment_object.nid
    comment_create_time = comment_object.create_time.strftime('%Y-%m-%d %H:%M')

    response_data = {}
    response_data['comment_id'] = comment_id
    response_data['comment_create_time'] = comment_create_time

    return HttpResponse(json.dumps(response_data))



