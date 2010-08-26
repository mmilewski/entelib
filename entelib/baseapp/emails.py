# -*- coding: utf-8 -*-

from django.template import loader, Context
from django.core.mail import send_mail as django_send_mail
from baseapp.models import Book, BookCopy, User, Reservation, EmailLog
from datetime import date, timedelta
from config import Config
from baseapp.utils import get_admins
from smtplib import SMTPRecipientsRefused


# _from_address = Config().get_str('mail_sender_address')   # is this one incorrect?
# _from_address = Config().get_str('default_email_sender')


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
    Sends emails. Parameters are defined like in django's send_mail.
    '''
    config = Config()
    if config.get_bool('log_send_emails'):
        log_email(sender, recipients, subject, msg)
    if config.get_bool('send_emails'):
        try:
            django_send_mail(subject, msg, sender, recipients)
        except SMTPRecipientsRefused:
            return 'Incorrect e-mail address - e-mail not sent'
    return None


def default_email(recipients, template, context, subject=None, sender=None):
    '''
    Desc:
        Sends email to recipients. Email is generated from template and context.

    Args:
        recipients: list of valid email addresses. Valid addresses are for example: "jasiu@onet.pl" or "Jan Kowalski <jan.kwlski@hotmail.com>"
        template: django template
        context: django.template.Context object
    '''
    t = loader.get_template(template)
    msg = t.render(context)
    sender = sender if sender else Config().get_str('default_email_sender')
    subject = subject if subject else Config().get_str('default_email_subject')
    send(subject, msg, sender, recipients)

def send_request_to_send_with_internal_post(reservation):
    recipients = list(reservation.book_copy.location.maintainer.all())
    template = 'email/send_with_internal_post_request'
    context = Context({'user' : reservation.for_whom,
               'reservation' : reservation,
              })
    default_email(recipients, template, context, subject='Internal-post-send request')


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


def user_registered(user):
    '''
    Desc:
        Send confirmation message to freshly registered user and notifies admin.
    Arg:
        user is User object
    '''
    tpl_for_user = 'email/registered'
    tpl_for_admin = 'email/activate'
    ctx = Context({'user' : user})
    reader = _make_recipient_from_user(user)
    default_email([reader], tpl_for_user, ctx)
    default_email(map(_make_recipient_from_user, get_admins()), tpl_for_admin, ctx)


def user_activated(user):
    '''
    Desc:
        Send notification to freshly activated user
    Arg:
        user is User object
    '''
    tpl = 'email/activated'
    ctx = Context({'user' : user})
    recipient = _make_recipient_from_user(user)
    default_email([recipient], tpl, ctx)
    

def password_reset(user, new_password):
    """
    Desc:
        Send email if user's password was reset. Usually this means usage of 'Forgot my password.
    Args:
        user - instance of User, whose password was reset. E-mail will be sent to him.
        new_password - new user's password. Not hashed. One will use this to log in. 
    """
    tpl = 'email/password_reset'
    context = Context({'new_password': new_password,
                       'user': user,
                       })
    recipient = _make_recipient_from_user(user)
    default_email([recipient], tpl, context)



