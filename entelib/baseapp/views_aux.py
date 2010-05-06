#-*- coding=utf-8 -*- 

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse #TODO usunąć ten wiersz kiedy forbidden będzie gotowe


def forbidden(request):
    return HttpResponse("Forbidden")

'''
tak będzie docelowo:
    return render_to_response(
       'forbidden.html',
       {},
       context_instance=RequestContext(request)
       )
'''

