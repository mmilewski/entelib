# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from baseapp.utils import pprint

# from django.contrib.auth.models import User as CustomUser  # don't !!
from django.contrib.auth.models import User
# from entelib.baseapp.models import CustomUser


class CustomUserModelBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(username=username)
            if user.check_password(password) or not settings.CHECK_PASSWORD_ON_AUTH:
                return user
#             user = User.objects.get(email=username)
#             if user.check_password(password) or not settings.CHECK_PASSWORD_ON_AUTH:
#                 return user
            return None     # None means auth failed
        except User.DoesNotExist:
            pprint("User %s doesn't exist" % username)
            return None


    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


# this tutorial was helpful:
# Extending the Django User model with inheritance
#     http://scottbarnham.com/blog/2008/08/21/extending-the-django-user-model-with-inheritance/
