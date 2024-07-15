from django.db import models
from django.utils import timezone

# Create your models here.
class student(models.Model):
    SEX_CHOICES = [
        ('M', '男'),
        ('F', '女'),
    ]
    cName = models.CharField('姓名',max_length=20, null=False, default='', primary_key=True)
    cPass = models.CharField('密碼',max_length=20, null=False, default='')
    cSex = models.CharField('性別',max_length=1, choices=SEX_CHOICES, default='', null=False)
    cBirthday = models.DateField('生日',null=False, default='')
    introduction = models.CharField('自介', max_length=300, default='')

    def __str__(self):
        return self.cName

class group(models.Model):
    id = models.IntegerField('序號', null=False, primary_key=True, default='')
    groupid = models.IntegerField('編號', null=False, default='')
    groupName = models.CharField('群組名',max_length=50, null=False, default='')
    member = models.CharField('成員',max_length=20, null=False, default='')
    isAdmin = models.BooleanField('是否為管理者', null=False, default='')

    def __str__(self):
        return self.groupid
    
class msg(models.Model):
    #id = models.IntegerField('編號', null=False, default='', primary_key=True)
    groupId = models.IntegerField('聊天室編號', null=False, default='')
    sender = models.CharField('發言者', null=False, default='')
    time = models.DateTimeField('時間', default=timezone.now)
    content = models.CharField('內容', null=False, default='', max_length=1000)
    reply = models.CharField('回應內容', default='')

    def __str__(self):
        return self.time

class forum(models.Model):
    id = models.IntegerField('編號', null=False, primary_key=True, default='')
    title = models.CharField('標題', max_length=100, null = False, default='')
    content = models.CharField('內文', max_length=1000, null = False, default='')
    name = models.CharField('發文者', max_length=20, null = False, default='')
    time = models.DateTimeField('保存日期',default = timezone.now)
    anonymous = models.BooleanField('匿名', default=0)
    types = models.CharField('類型', null=False, default='')

    def __str__(self):
        return self.id
    
class forumDiscussLike(models.Model):
    forumDiscussId = models.IntegerField('編號', null=False, default='')
    likePerson = models.CharField('按讚者', null=False, default='')

    def __str__(self):
        return self.likePerson

class forumDiscuss(models.Model):
    id = models.IntegerField('編號', primary_key=True, default='', null=False)
    forumId = models.IntegerField('討論版編號', null=False, default='')
    name = models.CharField('留言者', max_length=20, null = False, default='')
    content = models.CharField('留言', max_length=1000)
    time = models.DateTimeField('保存日期',default = timezone.now)
    anonymous = models.BooleanField('匿名', default=0)
    like = models.IntegerField('按讚數', default=0)

    def __str__(self):
        return self.forumId
    
class Following(models.Model):
    name = models.CharField('姓名',max_length=20, null=False, default='')
    following = models.CharField('追蹤',max_length=20, null=False, default='')

    def __str__(self):
        return self.name

class inviteToGroup(models.Model):
    groupid = models.IntegerField('編號', null=False, default='')
    invitor = models.CharField('邀請者', null=False, default='')
    receiver = models.CharField('受邀者', null=False, default='')

    def __str__(self):
        return self.groupid

class followRequest(models.Model):
    invitor = models.CharField('邀請者', null=False, default='')
    receiver = models.CharField('受邀者', null=False, default='')

    def __str__(self):
        return self.invitor
    
class inboxMsg(models.Model):
    receiver = models.CharField('通知者', max_length=20, null=False, default='')
    content = models.CharField('通知內容', max_length=500, null=False, default='')
    link = models.CharField('通知連結', default='')
    time = models.DateTimeField('時間', default = timezone.now)
    read = models.BooleanField('讀取與否', default=0)

    def __str__(self):
        return self.receiver