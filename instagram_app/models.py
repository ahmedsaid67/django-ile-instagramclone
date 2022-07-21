from asyncio import streams
from distutils.command.upload import upload
import imp
from pyexpat import model
from random import choices
import re
from secrets import choice
from statistics import mode
from tabnanny import verbose
from tkinter.tix import Tree
from turtle import pos, position
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save,post_delete
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import slugify
from django.urls import reverse
import os
from django.conf import settings
import uuid
from django.db.models import Max

from PIL import Image
from django.conf import settings
import os



class Tag(models.Model):
    title=models.CharField(max_length=75,verbose_name='Tag')
    slug=models.SlugField(null=False,blank=True,unique=True)

    class Meta:
        verbose_name_plural='Tags'
    
    def get_absolute_url(self):
        reverse("tags",arg=[self.slug])
    
    def __str__(self):
        return self.title
    
    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug=slugify(self.title)
        return super().save(*args,**kwargs)


def user_directory_path(instance,filename):
    return 'user_{0}/{1}'.format(instance.user.id,filename)


class PostFileContent(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE, related_name='content_owner')
    file=models.FileField(upload_to=user_directory_path)



class Post(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    content =  models.ManyToManyField(PostFileContent, related_name='contents')
    captions=models.TextField(max_length=1500,verbose_name='Caption')
    posted=models.DateTimeField(auto_now_add=True)
    tags=models.ManyToManyField(Tag,related_name="tags")
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    likes=models.IntegerField(default=0)

    def get_absolute_url(self):
        return reverse('postdetails', args=[str(self.id)])
    
    def __str__(self):
        return str(self.id)


def user1_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    profile_pic_name = 'user_{0}/profile.jpg'.format(instance.user.id)
    full_path = os.path.join(settings.MEDIA_ROOT, profile_pic_name)
    if os.path.exists(full_path):
        os.remove(full_path)
    return profile_pic_name

class Profile(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    first_name=models.CharField(max_length=50,null=True,blank=True)
    last_name=models.CharField(max_length=50,null=True,blank=True)
    location=models.CharField(max_length=50,null=True,blank=True)
    url=models.CharField(max_length=80,null=True,blank=True)
    profile_info=models.TextField(max_length=50,null=True,blank=True)
    crated=models.DateField(auto_now_add=True)
    favorites=models.ManyToManyField(Post,null=True,blank=True)
    picture=models.ImageField(upload_to=user1_directory_path, blank=True, null=True, verbose_name='Picture')


    def save(self,*args,**kwargs):
        super().save(*args,**kwargs)
        SIZE=250,250
        if self.picture:
            pic=Image.open(self.picture.path)
            pic.thumbnail(SIZE,Image.LANCZOS)
            pic.save(self.picture.path,"PNG")


def create_user_profile(sender,instance,created, **kwargs):
    if created:
        profil=Profile.objects.create(user=instance)
        profil.save()

def save_user_profile(sender,instance, **kwargs):
    try:
        instance.profile.save()
    except ObjectDoesNotExist:
        Profile.objects.create(user=instance)

post_save.connect(create_user_profile,sender=User)
post_save.connect(save_user_profile,sender=User)




class Follow(models.Model):
    follower=models.ForeignKey(User,on_delete=models.CASCADE,null=True,related_name="follower")
    following=models.ForeignKey(User,on_delete=models.CASCADE,null=True,related_name="following")
    
    def user_follow(sender,instance, *args , **kwargs):
        follow=instance
        sender=follow.follower
        following=follow.following
        notify=Notification(sender=sender,user=following, notification_type=3)
        notify.save()

    def user_unfollow(sender, instance, *args, **kwargs):
        follow=instance
        sender=follow.follower
        following=follow.following
        notify=Notification.objects.filter(sender=sender,user=following, notification_type=3)
        notify.delete()



post_save.connect(Follow.user_follow, sender=Follow)
post_delete.connect(Follow.user_unfollow, sender=Follow)


class Stream(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE,null=True, related_name='stream_following')
    user = models.ForeignKey(User, on_delete=models.CASCADE)   
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField()

    def add_post(sender,instance, *args, **kwargs):
        post=instance
        user=post.user
        followers=Follow.objects.filter(following=user)
        for follower in followers:
            stream= Stream(post=post,user=follower.follower, date=post.posted ,following=user)
            stream.save()



post_save.connect(Stream.add_post, sender=Post)


class Likes(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_like')
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_like')

	def user_liked_post(sender, instance, *args, **kwargs):
		like = instance
		post = like.post
		sender = like.user
		notify = Notification(post=post, sender=sender, user=post.user, notification_type=1)
		notify.save()

	def user_unlike_post(sender, instance, *args, **kwargs):
		like = instance
		post = like.post
		sender = like.user

		notify = Notification.objects.filter(post=post, sender=sender, notification_type=1)
		notify.delete()


post_save.connect(Likes.user_liked_post, sender=Likes)
post_delete.connect(Likes.user_unlike_post, sender=Likes)



class Notification(models.Model):
	NOTIFICATION_TYPES = ((1,'Like'),(2,'Comment'), (3,'Follow'))

	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="noti_post", blank=True, null=True)
	sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="noti_from_user")
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="noti_to_user")
	notification_type = models.IntegerField(choices=NOTIFICATION_TYPES)
	text_preview = models.CharField(max_length=90, blank=True)
	date = models.DateTimeField(auto_now_add=True)
	is_seen = models.BooleanField(default=False)




class Comment(models.Model):
    post=models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    body=models.TextField()
    date=models.DateTimeField(auto_now_add=True)

    def user_comment_post(sender, instance, *args, **kwargs):
        comment=instance
        post=comment.post
        text_preview=comment.body[:90]
        sender=comment.user
        notify=Notification(post=post, sender=sender, user=post.user, text_preview=text_preview, notification_type=2)
        notify.save()
    
    def user_del_comment_post(sender,instance, *args, **kwargs):
        like=instance
        post=like.post
        sender=like.user

        notify=Notification.objects.filter(post=post,sender=sender,notification_type=2)
        notify.delete()


post_save.connect(Comment.user_comment_post, sender=Comment)
post_delete.connect(Comment.user_del_comment_post, sender=Comment)



class Message(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE,related_name="user")
    sender=models.ForeignKey(User, on_delete=models.CASCADE,related_name="from_user")
    recipient=models.ForeignKey(User, on_delete=models.CASCADE,related_name="to_user")
    body=models.TextField(max_length=1000, null=True, blank=True)
    date=models.DateTimeField(auto_now_add=True)
    is_read=models.BooleanField(default=False)

    def sender_message(from_user,to_user,body):
        sender_message=Message(
            user=from_user,
            sender=from_user,
            recipient=to_user,
            body=body,
            is_read=True
        )
        sender_message.save()

        recipient_message=Message(
            user=to_user,
			sender=from_user,
			body=body,
			recipient=from_user,
        )
        recipient_message.save()

        return sender_message

    def get_message(user):
        users=[]
        messages=Message.objects.filter(user=user).values('recipient').annotate(Last=Max('date')).order_by('-Last')
        for message in messages:
            users.append({
            'user':User.objects.get(pk=message['recipient']),
            'last':message['Last'],
            'unread':Message.objects.filter(user=user,recipient__pk=message['recipient'], is_read=False).count()
        })

        return users


class StoryPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='story_post_user')
    content = models.FileField(upload_to=user_directory_path)

class Story(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='story_user')
	content = models.ManyToManyField(StoryPost,null=True,blank=True,related_name="story")
	caption = models.TextField(max_length=50)
	expired = models.BooleanField(default=False)
	posted = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.username


