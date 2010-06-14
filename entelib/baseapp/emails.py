#-*- coding=utf-8 -*-

from django.template import loader, Context
from django.core.mail import django_send_mail
from baseapp.models import Book, BookCopy, User, Reservation, EmailLog
from datetime import date, timedelta
from config import Config


_from_address = Config().get_str('mail_sender_address')


def log_email(sender, recipients, subject, body):
    '''
    Logs sent email.
    '''
    if not recipients:
        recipients = []
    assert(recipients)

    for recip in recipients:
        EmailLog(sender=sender, recipient=recip, subject=subject, body=body).save()


def send(subject, msg, sender, recipients):
    '''
    Sends emails. Parameters are defined like in send_mail.
    '''
    config = Config()
    if config.get_bool('log_send_email'):
        log_email(sender, recipients, subject, msg)
    if config.get_bool('send_email'):
        django_send_mail(subject, msg, sender, recipients)


def default_email(recipients, template, context, subject=None, sender=None):
    '''
    Desc:
        Sends email to recipients. Email is generated from template and context.

    Args:
        recipients: list of valid email adresses. Valid adresses are for example: "jasiu@onet.pl" or "Jan Kowalski <jan.kwlski@hotmail.com>"
        template: django template
        context: django.template.Context object
    '''

    t = loader.get_template(template)
    msg = t.render(context)
    sender = sender if sender else Config().get_str('default_email_sender')
    subject = subject if subject else 'NSN library notification'
    send(subject, msg, sender, recipients)


def notify_book_copy_available(reservation):
    t = 'rental_possible'
    c = Context({
           'title' :  reseration.book_copy.book.title,
           'authors' : [a.name for a in reservation.book_copy.book.authors],
           'deadline' : date.today() + timedelta(Config().get_int('reservation_rush'))
        })
    u = reservation.for_whom
    recipient = u'%s %s <%s>' % (u.first_name, u.last_name, u.email)
    default_email([recipient], t, c)
