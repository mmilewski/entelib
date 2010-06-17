#-*- coding=utf-8 -*-

from django.template import loader, Context
from django.core.mail import send_mail as django_send_mail
from baseapp.models import Book, BookCopy, User, Reservation, EmailLog
from datetime import date, timedelta
from config import Config


# _from_address = Config().get_str('mail_sender_address')   # is this one incorrect?
_from_address = Config().get_str('default_email_sender')


def log_email(sender, recipients, subject, body):
    '''
    Logs sent email.
    '''
    if not recipients:
        recipients = []
    assert(recipients)

    for recip in recipients:
        EmailLog(sender=sender, receiver=recip, subject=subject, body=body).save()


def send(subject, msg, sender, recipients):
    '''
    Sends emails. Parameters are defined like in send_mail.
    '''
    config = Config()
    if config.get_bool('log_send_emails'):
        log_email(sender, recipients, subject, msg)
    if config.get_bool('send_emails'):
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
    tpl = 'rental_possible'
    ctx = Context({
            'title'     : reservation.book_copy.book.title,
            'authors'   : [a.name for a in reservation.book_copy.book.author.all()],
            'deadline'  : date.today() + timedelta(Config().get_int('reservation_rush'))
            })
    recipient = _make_recipient_from_user(reservation.for_whom)
    default_email([recipient], tpl, ctx)


def made_reservation(reservation):
    '''
    Desc:
        Called if new reservation was added to db. Sends reservation confirmation.'
    Arg:
        reservation -- just added Reservation's instance.
    '''
    tpl = 'made_reservation'
    ctx = Context({
            'title'    : reservation.book_copy.book.title,
            'authors'  : [a.name for a in reservation.book_copy.book.author.all()],
            'deadline' : date.today() + timedelta(Config().get_int('reservation_rush'))
            })
    recipient = _make_recipient_from_user(reservation.for_whom)
    default_email([recipient], tpl, ctx)


def made_rental(rental):
    '''
    Desc:
        Called if new rental was added to db. Sends rental confirmation.'
    Arg:
        rental -- just added Rental's instance.
    '''
    tpl = 'made_rental'
    ctx = Context({
            'title'    : rental.reservation.book_copy.book.title,
            'authors'  : [a.name for a in rental.reservation.book_copy.book.author.all()],
            'deadline' : 'TODO: what should I put here?'
            })
    recipient = _make_recipient_from_user(rental.reservation.for_whom)
    default_email([recipient], tpl, ctx)


def _make_recipient_from_user(user_instance):
    u = user_instance
    return u'%s %s <%s>' % (u.first_name, u.last_name, u.email)
