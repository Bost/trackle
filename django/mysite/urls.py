# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
#from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static


from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^polls/', include('polls.urls')),
    #url(r'^list/', include('polls.urls')),
    url(r'^admin/', include(admin.site.urls)),
    #(r'^', include('myapp.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


