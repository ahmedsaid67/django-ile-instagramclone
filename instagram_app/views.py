from ast import arg
import imp
from multiprocessing import context
from tkinter import S
from venv import create
from django.urls import reverse
from turtle import pos, title
from django.shortcuts import render,redirect,get_object_or_404
from django.test import tag

from .forms import UserRegisterForm,EditForm,NewPostForm,CommentForm,NewStoryForm
from django.contrib.auth import authenticate,login as login_,logout as logout_
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Post,Likes, PostFileContent,Stream,Follow, Tag,Profile, Comment, Message, Notification,Story,StoryPost
from django.http import (HttpResponse, HttpResponseBadRequest, 
                         HttpResponseForbidden, JsonResponse)
from django.db.models import Q
from django.http import JsonResponse
from datetime import datetime,timedelta
from .task import *
from itertools import chain


@login_required(login_url="login")
def index(request):
    user=request.user
    posts=Stream.objects.filter(user=user)
    group_ids=[]
    user_list=[]
    storie_list=[]
    for post in posts:
        group_ids.append(post.post.id)
    
    post_items=Post.objects.filter(id__in=group_ids).all().order_by('-posted')



    fallows=Follow.objects.filter(follower=user)
    

    for fallow in fallows:
        user_list.append(fallow.following)
    
    
    for userlist in user_list:
        story=Story.objects.filter(user=userlist)
        storie_list.append(story)

    feed_lists=list(chain(*storie_list))
   

    stor_list=[]

    for stor in storie_list:
        for s in stor:
            stor_list.append(s.user)
    

    list_stor=list()
    for stori in stor_list:
        if stori not in list_stor:
            list_stor.append(stori)
    
    
    storicdict={}

    for storic in list_stor:
        storicdict[storic]= Story.objects.filter(user=storic)
    

    
    CheckStoriesDate()

    DeleteExpired()
    
    return render(request,"index.html",{"post_items":post_items,"stories":storicdict})


@login_required(login_url="login")
def NewPost(request):
    user=request.user.id
    user1=request.user
    tags_obj=[]
    files_object=[]



    if request.method=="POST":
        form=NewPostForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('content')
            print(files)
            captions=form.cleaned_data.get("captions")
            tags_form=form.cleaned_data.get("tags")
            
            tags_list=tags_form.split(",")
            for tags in tags_list:
                tag, create=Tag.objects.get_or_create(title=tags)
                tags_obj.append(tag)

            for file in files:           
                file_instance= PostFileContent(file=file,user=user1)
                file_instance.save()
                files_object.append(file_instance)

            post, create1=Post.objects.get_or_create(captions=captions,user_id=user)
            post.tags.set(tags_obj)
            post.content.set(files_object)
            post.save()

            print(post.content.all())
            return redirect("index")

    form=NewPostForm
    return render(request,"newpost.html",{"form":form})


@login_required(login_url="login")
def PostDetails(request,post_id):
    user=request.user
    post=get_object_or_404(Post, id=post_id)

    comments=Comment.objects.filter(post=post).order_by('date')

    if request.method=="POST":
        form=CommentForm(request.POST)
        if form.is_valid():
            comment=form.save(commit=False)
            comment.post=post
            comment.user=user
            comment.save()
            return redirect(reverse('postdetails',args=[post_id]))
    else:
        form=CommentForm()


    profile=Profile.objects.get(user=request.user)
    favorited=False
    if profile.favorites.filter(id=post_id).first():
        favorited=True


    context={
        "post":post,
        "favorited":favorited,
        "form":form,
        "comments":comments
    }
    return render(request,"post_detail.html",context)


@login_required(login_url="login")
def tags(request,tag_slug):
    tag=get_object_or_404(Tag, slug=tag_slug)
    posts=Post.objects.filter(tags=tag).order_by('-posted')
    context={
        "tag":tag,
        "posts":posts
    }
    return render(request,"tag.html",context)


@login_required(login_url="login")
def like(request,post_id):
    user=request.user
    post=Post.objects.get(id=post_id)
    print(post)
    print(post)
    like=Likes.objects.filter(user=user,post=post).first()
    if like is None:
        like=Likes.objects.create(user=user,post=post)
        like.save()
        post.likes+=1
        post.save()
    else:
        like.delete()
        post.likes-=1
        post.save()
    return redirect("index")


@login_required(login_url="login")
def liked(request,post_id):
    user=request.user
    post=Post.objects.get(id=post_id)
    like=Likes.objects.filter(user=user,post=post).first()
    if like is None:
        like=Likes.objects.create(user=user,post=post)
        like.save()
        post.likes+=1
        post.save()
    else:
        like.delete()
        post.likes-=1
        post.save()
    return redirect(reverse('postdetails', args=[post_id]))


@login_required(login_url="login")
def favorite(request,post_id):
    user=request.user
    post=Post.objects.get(id=post_id)
    profile=Profile.objects.get(user=user)

    if profile.favorites.filter(id=post_id).first():
        profile.favorites.remove(post)
    else:
        profile.favorites.add(post)

    return redirect(reverse('postdetails', args=[post_id]))

from django.urls import resolve
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required(login_url="login")
def UserProfile(request,username):
    user=get_object_or_404(User,username=username)

    profile=Profile.objects.get(user=user)
    url_name=resolve(request.path).url_name

    if url_name=="profile":
        posts=Post.objects.filter(user=user).order_by("-posted")
    else:
        posts=profile.favorites.all()

    posts_count = Post.objects.filter(user=user).count()
    following_count=Follow.objects.filter(follower=user).count()
    followers_count=Follow.objects.filter(following=user).count()
	
    follow_status=Follow.objects.filter(following=user, follower=request.user).exists()

    posts1 = Paginator(posts, 4)  
    page_number = request.GET.get('page')
    print(page_number)
    
    page_obj = posts1.get_page(page_number)  

    print(page_obj)

    print(page_obj.next_page_number)
    
    context = {
		'page_obj': page_obj,
		'profile':profile,
		'following_count':following_count,
		'followers_count':followers_count,
		'posts_count':posts_count,
		'follow_status':follow_status,
		'url_name':url_name,
	}

    return render(request,"profile.html",context)


from django.db import transaction



def follow(request,username,option):
    user=request.user
    following=get_object_or_404(User,username=username)

    try:
        f, created=Follow.objects.get_or_create(follower=user,following=following)

        if int(option)==0:
            f.delete()
            Stream.objects.filter(following=following,user=user).all().delete()
        else:
            posts=Post.objects.filter(user=following)[:10]
            with transaction.atomic():
                for post in posts:
                    stream=Stream.objects.create(post=post,user=user,date=post.posted,following=following)
                    stream.save()
        return redirect(reverse('profile',args=[username]))
    except User.DoesNotExist():
        return redirect(reverse('profile',args=[username]))


@login_required(login_url="login")
def  editProfile(request,username):
    
    profile=Profile.objects.get(user__username=username)
    print(profile.picture)
    if request.method=="POST":
        form=EditForm(request.POST,request.FILES)
        if form.is_valid():
            if form.cleaned_data.get("picture") !=None :
                profile.first_name=form.cleaned_data.get("first_name")
                
                profile.picture = form.cleaned_data.get('picture')
                print(profile.picture)
                profile.last_name=form.cleaned_data.get("last_name")
                profile.location=form.cleaned_data.get("location")
                profile.url=form.cleaned_data.get("url")
                profile.profile_info=form.cleaned_data.get("profile_info")
                profile.save() 
            else:
                profile.first_name=form.cleaned_data.get("first_name")
                profile.last_name=form.cleaned_data.get("last_name")
                profile.location=form.cleaned_data.get("location")
                profile.url=form.cleaned_data.get("url")
                profile.profile_info=form.cleaned_data.get("profile_info")
                profile.save()
            return redirect('index')
    else:
        form=EditForm()

    return render(request,"edit_profile.html",{"form":form})




def login(request):
    if request.method=="POST":
        username=request.POST["username"]
        password=request.POST["password"]
        user_login=authenticate(username=username,password=password)
                
        
        if user_login is not None:
            login_(request,user_login)
            return redirect("index")
        else:
            messages.info(request,"Credentials Invalid")
            return redirect('login')
    else:
        return render(request,"login.html")

def signup(request):
    if request.method=="POST":
        form=UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data.get("username")
            password=form.cleaned_data.get("password1")
            user=authenticate(username=username,password=password)
            login_(request,user)
            messages.success(request, 'Account created ')
            return redirect("edit-profile")
        
    form = UserRegisterForm()
    return render(request, 'signup.html',{'form':form})

@login_required(login_url="login")
def logout(request):
    logout_(request)
    return redirect("login")



@login_required(login_url="login")
def Inbox(request):
	messages = Message.get_message(user=request.user)
	active_direct = None
	directs = None

	if messages:
		message = messages[0]
		active_direct = message['user'].username
		directs = Message.objects.filter(user=request.user, recipient=message['user'])
        
		directs.update(is_read=True)
		for message in messages:
			if message['user'].username == active_direct:
				message['unread'] = 0

	context = {
		'directs': directs,
		'messages': messages,
		'active_direct': active_direct,
		}

    

	return render(request, "direct.html", context)



@login_required(login_url="login")
def Directs(request, username):
	user = request.user
	messages = Message.get_message(user=user)
	active_direct = username
	directs = Message.objects.filter(user=user, recipient__username=username)
	directs.update(is_read=True)
	for message in messages:
		if message['user'].username == username:
			message['unread'] = 0

	context = {
		'directs': directs,
		'messages': messages,
		'active_direct':active_direct,
	}

	return render(request, "direct.html", context)


@login_required(login_url="login")
def SendDirect(request):
	from_user = request.user
	to_user_username = request.POST.get('to_user')
	body = request.POST.get('body')
	
	if request.method == 'POST':
		to_user = User.objects.get(username=to_user_username)
		Message.sender_message(from_user, to_user, body)
		return redirect('Inbox')
	else:
		HttpResponseBadRequest()


@login_required(login_url="login")
def usersearch(request):
    q=request.GET.get("q")
    if q:

        users=User.objects.filter(Q(username__icontains=q))
        paginator=Paginator(users,3)
        page_number=request.GET.get("page")
        users_paginator=paginator.get_page(page_number)

        context={
            "users":users_paginator
        }
        return render(request, "search_user.html",context)
        
    return render(request, "search_user.html")


@login_required(login_url="login")
def NewConversation(request,username):
    from_user=request.user
    body="Says hello"
    try:
        to_user=User.objects.get(username=username)
    except Exception as e:
        return redirect("usersearch")
    if from_user!=to_user:
        Message.sender_message(from_user,to_user,body)
    return redirect("Inbox")

def checkDirects(request):
    directs_count=0
    if request.user.is_authenticated:
        directs_count=Message.objects.filter(user=request.user,is_read=False).count()
    
    return { 'direct_count':directs_count}


def ShowNOtifications(request):
	user = request.user
	notifications = Notification.objects.filter(user=user).order_by('-date')
	Notification.objects.filter(user=user, is_seen=False).update(is_seen=True)

	context = {
		'notifications': notifications,
	}

	return render(request, "notifications.html", context)



def DeleteNotification(request,noti_id):
    user = request.user
    Notification.objects.filter(id=noti_id,user=user).delete()
    print(noti_id)
    return redirect('shownotifications')


def countnotifications(request):
    count_notifications = 0
    if request.user.is_authenticated:
        count_notifications= Notification.objects.filter(user=request.user,is_seen=False).count()

    return {'count_notifications':count_notifications}


@login_required
def NewStory(request):
    user=request.user
    file_obj=[]

    if request.method == "POST":
        form=NewStoryForm(request.POST, request.FILES)
        if form.is_valid():
            files=request.FILES.getlist('content')
            caption=form.cleaned_data.get('caption')
            for file in files:
                storipost= StoryPost(user=user,content=file)
                storipost.save()
                file_obj.append(storipost)

            story, post1=Story.objects.get_or_create(user=user,caption=caption)

            print(story)
            print(file_obj)
            story.content.set(file_obj)
            story.save()
            print("storie")
            print(story.content.all())
            return redirect("index")

    else:
        form= NewStoryForm()

    context={
        'form':form
    }

    return render(request, 'new_story.html', context)
