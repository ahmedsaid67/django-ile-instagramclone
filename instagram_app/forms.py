from pyexpat import model
from statistics import mode
from attr import field, fields
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms import ModelForm
from .models import Post, Profile , Comment,Story
from django.forms import ClearableFileInput


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "class":"bg-gray-200 mb-2 shadow-none dark:bg-gray-800 ",
            "style":"",
        })
        self.fields["email"].widget.attrs.update({
            "class":"bg-gray-200 mb-2 shadow-none dark:bg-gray-800 "
        })
        self.fields["password1"].widget.attrs.update({
            "class":"bg-gray-200 mb-2 shadow-none dark:bg-gray-800"
        })
        self.fields["password2"].widget.attrs.update({
            "class":"bg-gray-200 mb-2 shadow-none dark:bg-gray-800",
        })

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class RegisterForm(ModelForm):

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'style':'color:red'}))
    password = forms.CharField(widget=forms.PasswordInput())
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "messages":"Please enter your name"
        })
    class Meta:
        model= User
        fields = '__all__'
       

class NewPostForm(ModelForm):
    content=forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple':True}), required=True)
    captions=forms.CharField(widget=forms.Textarea(attrs={'class':'input is-medium'}), required=True)
    tags=forms.CharField(widget=forms.TextInput(attrs={'class':'input is-medium'}), required=True)

    class Meta:
        model=Post
        fields=("content","captions","tags")

class EditForm(ModelForm):
    picture=forms.ImageField(required=False)
    first_name=forms.CharField(widget=forms.TextInput(attrs={'class':'input is-medium'}), required=False)
    last_name=forms.CharField(widget=forms.TextInput(attrs={'class':'input is-medium'}), required=False)
    location=forms.CharField(widget=forms.TextInput(attrs={'class':'input is-medium'}), required=False)
    url=forms.URLField(widget=forms.TextInput(attrs={'class':'input is-medium'}), required=False)
    profile_info=forms.CharField(widget=forms.Textarea(attrs={'class':'input is-medium'}), required=False)
    class Meta:
        model=Profile
        fields=("picture","first_name","last_name","location","url","profile_info")


class CommentForm(ModelForm):
    body =forms.CharField(widget=forms.Textarea(attrs={'class':'input is-medium'}), required=False)
    class Meta:
        model=Comment
        fields=('body',)



class NewStoryForm(forms.ModelForm):
	content = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=True)
	caption = forms.CharField(widget=forms.Textarea(attrs={'class': 'input is-medium'}), required=True)

	class Meta:
		model = Story
		fields = ('content', 'caption')