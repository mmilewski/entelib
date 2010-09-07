# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
import settings

urlpatterns = patterns('',
    (r'^entelib/', include('entelib.baseapp.urls')),
    (r'^' + settings.MEDIA_URL[1:] + '(?P<path>.*)$',  'django.views.static.serve',  { 'document_root': settings.MEDIA_ROOT, }),
    (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/entelib/'}),
)


if settings.IS_DEV:
    from django.contrib.auth import authenticate, login
    from django.contrib.auth.models import User
    from django.http import HttpResponseRedirect

    def _login_user(request):
        user = authenticate(username='user', password='user')
        login(request, user)
        return HttpResponseRedirect('/')
    def _login_lib(request):
        user = authenticate(username='lib', password='lib')
        login(request, user)
        return HttpResponseRedirect('/')
    def _login_admin(request):
        user = authenticate(username='admin', password='admin')
        login(request, user)
        return HttpResponseRedirect('/')

    urlpatterns += patterns('',
        (r'_login_user', 'entelib.urls._login_user'),
        (r'_login_lib', 'entelib.urls._login_lib'),
        (r'_login_admin', 'entelib.urls._login_admin'),
    )
