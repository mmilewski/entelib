from django.conf import settings
from django.db import connection
from django.template import Template, Context
from django.http import HttpResponseRedirect
from django.contrib import messages
from entelib.baseapp.models import Feedback

class FeedbackMiddleware:
    def process_request(self, request):
        if (request.method == 'POST') and ('btn_feedback_commit' in request.POST):
            post = request.POST
            source = request.path
            if source.startswith('//') :
                source = source[1:]
            who = post['feedback_user']
            msg = source + '\n' + post['feedback_msg']
            meta = request.META
            agent = 'unknown'
            if 'HTTP_USER_AGENT' in meta:
                agent = meta['HTTP_USER_AGENT']
            Feedback.objects.create(who=who, msg=msg, agent=agent)
            messages.info(request, 'Thank you for your feedback')
            response = HttpResponseRedirect(source)
            return response

    def process_response (self, request, response):
        return response
