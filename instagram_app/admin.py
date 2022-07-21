from atexit import register
from django.contrib import admin
from .models import Follow, Profile,Tag,Post,Follow,Stream,Likes,Comment,Message,PostFileContent,Story,StoryPost

class tagAdmin(admin.ModelAdmin):
    prepopulated_fields={"slug":("title",)}

admin.site.register(Profile)
admin.site.register(Tag,tagAdmin)
admin.site.register(Post)
admin.site.register(Follow)
admin.site.register(Stream)
admin.site.register(Likes)
admin.site.register(Comment)
admin.site.register(Message)
admin.site.register(PostFileContent)
admin.site.register(Story)
admin.site.register(StoryPost)
