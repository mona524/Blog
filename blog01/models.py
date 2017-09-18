from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import time

class ArticleManager(models.Manager):
    def archive(self,**kwargs):
        l = []
        for i in self.filter(**kwargs).values('create_time'):
            date = i['create_time']
            time1 = date.strftime('%Y-%m')
            l.append(time1)
        return l


class UserAdmin(BaseUserManager):
    def archive(self,**kwargs):
        time1 = self.filter(**kwargs).values('create_time')
        l = []
        for i in time1:
            tim2=i['create_time']

            tim3 = tim2.timestamp()
            t = time.time()-tim3
            t2 = int(t/(60*60)/24)
            t3 = int(((t/(60*60))/24-t2)*24)
            l.append(t2)
            l.append(t3)
        return l

class UserInfo(AbstractUser):
    """
    用户信息
    """
    nid = models.BigAutoField(primary_key=True)
    nickname = models.CharField(verbose_name='昵称', max_length=32)
    telephone = models.CharField(max_length=11, blank=True, null=True, unique=True, verbose_name='手机号码')
    #blank=Ture 设置Django自带到user表里该字段可为空，null=True是Userinfo表里该字段为空，因为继承里User表，必须两者都设置，该字段才可以为空
    avatar = models.FileField(verbose_name='头像', upload_to='./upload/avatar/') #upload_to 设置上传文件的路径（如果设置了media,则传到media文件下，如果没有，则放在根目录下）
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True) #自动添加该字段

    fans = models.ManyToManyField(verbose_name='粉丝们',
                                  to='UserInfo', #设置多对多关联表
                                  through='UserFans', #指定关联的第三张表（自己创建），如果不指定，会自动创建第三张关系表，但是查询数据时不能使用该表，谷自己创建，
                                  through_fields=('user', 'follower')) #关联的字段

    objects = UserAdmin()


    def __str__(self):
        return self.username

class UserFans(models.Model):
    """
    互粉关系表
    """
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey(verbose_name='博主', to='UserInfo', to_field='nid', related_name='users')
    follower = models.ForeignKey(verbose_name='粉丝', to='UserInfo', to_field='nid', related_name='followers')

    class Meta:
        unique_together = [
            ('user', 'follower'), #联合主键
        ]

class Blog(models.Model):
    """
    博客信息
    """
    nid = models.BigAutoField(primary_key=True)
    title = models.CharField(verbose_name='个人博客标题', max_length=64)
    site = models.CharField(verbose_name='个人博客后缀', max_length=32, unique=True)
    theme = models.CharField(verbose_name='博客主题', max_length=32)
    user = models.OneToOneField(to='UserInfo', to_field='nid') #建立一对一的关系

    def __str__(self):
        return self.title

class Category(models.Model):
    """
    博主个人文章分类表
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='分类标题', max_length=32)
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid')

    def __str__(self):
        return self.title

class Article(models.Model):
    nid = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=50, verbose_name='文章标题')
    desc = models.CharField(max_length=255, verbose_name='文章描述')
    read_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    up_count = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)
    category = models.ForeignKey(verbose_name='文章类型', to='Category', to_field='nid', null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid')
    tags = models.ManyToManyField(
        to="Tag",
        through='Article2Tag',
        through_fields=('article', 'tag'),
    )

    type_choices = [
        (1, "Python"),
        (2, "Linux"),
        (3, "OpenStack"),
        (4, "GoLang"),
    ]

    article_type_id = models.IntegerField(choices=type_choices, default=None)
    objects = ArticleManager()

    def __str__(self):
        return self.title

class ArticleDetail(models.Model):
    """
    文章详细表
    """
    nid = models.AutoField(primary_key=True)
    content = models.TextField(verbose_name='文章内容', )
    article = models.OneToOneField(verbose_name='所属文章', to='Article', to_field='nid')



class Comment(models.Model):
    """
    评论表
    """
    nid = models.BigAutoField(primary_key=True)
    article = models.ForeignKey(verbose_name='评论文章', to='Article', to_field='nid')
    content = models.CharField(verbose_name='评论内容', max_length=255)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    parent_id = models.ForeignKey('self', blank=True, null=True, verbose_name='父级评论')
    user = models.ForeignKey(verbose_name='评论者', to='UserInfo', to_field='nid')
    up_count = models.IntegerField(default=0,null=True,blank=True)

    def __str__(self):
        return self.content

class ArticleUpDown(models.Model):
    """
    点赞表
    """
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey('UserInfo', null=True)
    article = models.ForeignKey("Article", null=True)
    models.BooleanField(verbose_name='是否赞')

class CommentUp(models.Model):
    """
    点赞表
    """
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey('UserInfo', null=True)
    comment = models.ForeignKey("Comment", null=True)

class Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='标签名称', max_length=32)
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid')

    def __str__(self):
        return self.title

class Article2Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(verbose_name='文章', to="Article", to_field='nid')
    tag = models.ForeignKey(verbose_name='标签', to="Tag", to_field='nid')

    class Meta:
        unique_together = [
            ('article', 'tag'),
        ]




class Form_info(forms.Form):
    def validate_name(value):
        try:
            User.objects.get(username=value)
            raise ValidationError('%s 的信息已经存在!'%value)
        except User.DoesNotExist:
            pass
    username = forms.CharField(validators=[validate_name],min_length=3,error_messages={'required':'用户名不能为空'})
    password = forms.CharField(min_length=4,error_messages={'required':'密码不能为空'},widget=forms.PasswordInput)







