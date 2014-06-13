from django.db import models
import datetime
from django.utils import timezone
from django.contrib.auth.models import User


# Create your models here.
class Poll(models.Model):
    author = models.ForeignKey(User)
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField("Date published")

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) < self.pub_date < now

    def __unicode__(self):
        return self.question

    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'


class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __unicode__(self):
        return self.choice_text


class Vote(models.Model):
    choice = models.ForeignKey(Choice)
    user = models.ForeignKey(User)
