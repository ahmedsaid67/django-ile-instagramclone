import imp
from celery import shared_task
from .models import Follow,Story,StoryPost
from itertools import chain
from datetime import datetime, timedelta


@shared_task
def test_func(user,user_list,storie_list,stor_list,storicdict):
    fallows=Follow.objects.filter(follower=user)
    

    for fallow in fallows:
        user_list.append(fallow.following)
    
    
    for userlist in user_list:
        story=Story.objects.filter(user=userlist)
        storie_list.append(story)

    feed_lists=list(chain(*storie_list))
   

    

    for stor in storie_list:
        for s in stor:
            stor_list.append(s.user)
    

    list_stor=list()
    for stori in stor_list:
        if stori not in list_stor:
            list_stor.append(stori)

    

    for storic in list_stor:
        storicdict[storic]= Story.objects.filter(user=storic)



@shared_task
def CheckStoriesDate():
    exp_date=datetime.now() - timedelta(hours=1)
    old_storie=Story.objects.filter(posted__gt=exp_date)
    old_storie.update(expired=True)
    print("storied update")


@shared_task
def DeleteExpired():
    Story.objects.filter(expired=True).delete()
    StoryPost.objects.filter(story=None).delete()