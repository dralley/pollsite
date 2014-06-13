from django.conf.urls import patterns, include, url
from django.contrib import admin
import polls.urls

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pollsite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^polls/', include(polls.urls, namespace="polls")),
)
