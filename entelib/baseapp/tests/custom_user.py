from django.test import TestCase
from page_logger import *

from baseapp.models import CustomUser


class CustomUserTest(TestCase, PageLogger):
    def test_shoe_size(self):
        self.login()
        try:
            user = CustomUser.objects.get(username=self.username)
        except CustomUser.DoesNotExist, e:
            self.assert_(False and 'User must exist here. Something strange happend.')
