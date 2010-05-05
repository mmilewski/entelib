# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.backends import ModelBackend

# from django.contrib.auth.models import User    # don't !!
from entelib.baseapp.models import CustomUser


class CustomUserModelBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        try:
            user = CustomUser.objects.get(username=username)
            if user.check_password(password) or not settings.CHECK_PASSWORD_ON_AUTH:
                return user
            else:
                return None     # None means auth failed
        except CustomUser.DoesNotExist:
            print 'User %s doesnt exist' % username
            return None


    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None


# this tutorial was helpful:
# Extending the Django User model with inheritance
#     http://scottbarnham.com/blog/2008/08/21/extending-the-django-user-model-with-inheritance/
