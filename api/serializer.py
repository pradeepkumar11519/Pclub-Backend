from rest_framework import serializers
from .models import *
from .helpers import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email','username','password')
    def create(self, data):
        user = User.objects.create(
            email=data.get('email'),
            password = data.get('password'),
            username=data.get('username'),
            )
        user.set_password(data.get('password'))
        user.save()
        return user
    def validate(seld,data):
        user_email = User.objects.filter(email=data.get('email')).exists()
        if user_email:
            raise serializers.ValidationError({'error':'Email Already Exists Try With Another'})
        else:
            return data 

    
class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields =  "__all__"
    def create(self,data):
        user = self.context['request'].user
        blog = Blog.objects.create(
            user = user,
            title = data.get('title'),
            desc = data.get('desc'),
            image = data.get('image'),
            datestamp = getdate(),
            timestamp = gettime(),
        )
        blog.save()
        return blog


class VerifyOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email_is_verified","otp","email")



class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogComment
        fields = "__all__"
    def create(self,data):
        if data.get('parent'):
            parentname = data.get('parent').user.username
            parentcomment = data.get('parent').comment
        else:
            parentname = None
            parentcomment = None
        comment = BlogComment.objects.create(comment = data.get('comment'),user = data.get("user"),parent = data.get("parent"),datestamp = getdate(),timestamp=gettime(),parent_name = parentname,parent_comment = parentcomment,blog=data.get('blog'))
        comment.save()
        return comment