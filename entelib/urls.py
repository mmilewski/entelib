# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()


# Czy to jest do czegoś potrzebne? Tak
def quickhack(request):
    from entelib.baseapp.models import BookCopy
    from django.http import HttpResponse
    from django.template import Context, Template
    copies = BookCopy.objects.all()
    t = Template("""
           {% for copy in copies %}  {{ copy.book.title }}, {{ copy.location }}  {% endfor %}
           <hr/>
           {% for xs in xss %} {% for x in xs %} {{ x }} {% endfor %} <br/>{% endfor %}
         """)
    html = t.render(Context({'copies':copies,'xss': [[1,2,3,4],[4,5],[6,7,8,9,10,11,12]]}))
    return HttpResponse(html)


urlpatterns = patterns('',
    (r'^quickhack', 'entelib.urls.quickhack'),
    (r'^entelib/', include('entelib.baseapp.urls')),
    (r'^' + settings.MEDIA_URL[1:] + '(?P<path>.*)$',  'django.views.static.serve',  { 'document_root': settings.MEDIA_ROOT, }),
    (r'^$', 'django.views.generic.simple.redirect_to', {'url': '/entelib/'}),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
