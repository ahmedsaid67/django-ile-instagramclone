from django.contrib import admin
from django.urls import path,include
from . import views


urlpatterns = [
    path('login/',views.login,name="login"),
    path('logout/',views.logout,name="logout"),
    path('signup/',views.signup,name="signup"),
    path('index/',views.index,name="index"),
    path('newpost/',views.NewPost,name="newpost"),
    path('<uuid:post_id>',views.PostDetails,name="postdetails"),
    path('tag/<slug:tag_slug>',views.tags,name="tags"),
    path('like/<uuid:post_id>',views.like,name="like"),
    path('liked/<uuid:post_id>',views.liked,name="liked"),
    path('favorite/<uuid:post_id>',views.favorite,name="favorite"),
    path('newstory/',views.NewStory,name="newstory"),
]