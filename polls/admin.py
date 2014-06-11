from django.contrib import admin
from polls.models import Poll, Choice


# Register your models here.
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class PollAdmin(admin.ModelAdmin):
    fields = [(None,               {'fields': ['question']}),
              ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
              ]
    inlines = ChoiceInline
    list_display = ('question', 'pub_date')


admin.site.register(Poll, PollAdmin)
admin.site.register(Choice)
