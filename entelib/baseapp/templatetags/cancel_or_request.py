#-*- coding=utf-8 -*- 

from django import template

register = template.Library()

@register.inclusion_tag('tags/cancel_or_request.html', takes_context=True)
def cancel_or_request_form(context):
    return { 'cancelled_or_requested_reservation' : context['reserved']['reservation'],
             'send_possible' : context['reserved']['send_possible'],
             }
