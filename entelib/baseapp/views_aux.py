#-*- coding=utf-8 -*- 

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect #TODO usunąć HttpResponse 

def render_response(request, template, dict={}):
    if request.user.has_perm('baseapp.list_users'): 
        dict.update( { 'can_list_users' : 'True' } )
    return render_to_response(
        template,
        dict,
        context_instance=RequestContext(request)
    )

def render_forbidden(request):
    if request.user.is_authenticated():
        return HttpResponse("Forbidden")
    else:
        return HttpResponseRedirect('/entelib/login/')
        

'''
tak będzie docelowo:
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/entelib/login/')
    return render_to_response(
       'forbidden.html',
       {},
       context_instance=RequestContext(request)
    )
'''

