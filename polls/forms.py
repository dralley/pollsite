from django import forms
from polls import models
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


# class PollForm(forms.ModelForm):

#     class Meta:
#         model = models.Poll
#         fields = ('question')