"""instagram_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from . import settings
from django.conf.urls.static import static
from instagram_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/',include("instagram_app.urls")),
    path('<str:username>',views.UserProfile, name="profile"),
    path('<str:username>/saved',views.UserProfile, name="profilefavorites"),
    path('<str:username>/follow/<str:option>',views.follow, name="follow"),
    path('<str:username>/edit_profile',views.editProfile, name="edit_profile"),
    path('inbox/',views.Inbox,name="Inbox"),
    path('direct/<username>',views.Directs,name="direct"),
    path('senddirect/',views.SendDirect,name="send_direct"),
    path('usersearch/',views.usersearch,name="usersearch"),
    path('newconversation/<str:username>',views.NewConversation, name="newconversation"),
    path('shownotifications/',views.ShowNOtifications,name="shownotifications"),
    path('shownotifications/<noti_id>/delete',views.DeleteNotification,name="DeleteNotification"),
    
]

urlpatterns += static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)