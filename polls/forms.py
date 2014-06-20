from django import forms
from polls import models
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class PollForm(forms.ModelForm):

    choice1 = forms.CharField(max_length=128, required=True)
    choice2 = forms.CharField(max_length=128, required=True)
    choice3 = forms.CharField(max_length=128, required=False)
    choice4 = forms.CharField(max_length=128, required=False)
    choice5 = forms.CharField(max_length=128, required=False)

    def save(self, *args, **kwargs):
        poll = super(PollForm, self).save(*args, **kwargs)

        choices = sorted([text for name, text in self.cleaned_data.items() if name.startswith('choice') and text != ''])

        for choice in choices:
            poll.choice_set.create(choice_text=choice)

        return poll

    class Meta:
        model = models.Poll
        fields = ('question', 'author', 'pub_date')
        widgets = {
            'pub_date': forms.HiddenInput,
            'author': forms.HiddenInput,
        }
        labels = {
            'question': "What is your question?"
        }
