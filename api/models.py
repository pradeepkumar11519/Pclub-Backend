from django.db import models
from django.contrib.auth.models import AbstractUser
from .helpers import *

def Blog_path(instance,filename):
    return 'BlogImages/user_{0}/{1}'.format(instance.user,filename)

# Create your models here.
class User(AbstractUser):
    email_is_verified = models.BooleanField(null=True,default=False,blank=True)
    otp = models.CharField(max_length=10,null=True,blank=True,default=None)
    
    REQUIRED_FIELDS = []

class Blog(models.Model):
    user = models.ForeignKey(User,null=True,blank=True,default=None,to_field="username",on_delete=models.CASCADE)
    title = models.CharField(max_length=225,null=True,blank=True,default=None)
    desc = models.TextField(null=True,blank=True,default=None)
    datestamp = models.CharField(max_length=225,null=True,blank=True,default=getdate())
    timestamp = models.CharField(max_length=225,null=True,blank=True,default=gettime())
    image = models.ImageField(null=True,blank=True,default=None,upload_to=Blog_path)



class BlogComment(models.Model):
    comment = models.TextField(default=None,null=True,blank=True)
    user = models.ForeignKey(User,to_field="username",on_delete=models.CASCADE,null=True,blank=True,default=None)
    blog = models.ForeignKey(Blog,on_delete=models.CASCADE,null=True,blank=True,default=None)
    parent = models.ForeignKey('self',on_delete=models.CASCADE,null=True,blank=True,default=None)
    parent_name = models.CharField(max_length=225,null=True,blank=True,default=None)
    parent_comment = models.TextField(null=True,blank=True,default=None)
    datestamp = models.CharField(max_length=225,default=None,null=True,blank=True)
    timestamp = models.CharField(max_length=225,default=None,null=True,blank=True)