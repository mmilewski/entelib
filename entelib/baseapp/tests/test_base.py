#-*- coding=utf-8 -*- 
from django.test import TestCase
from baseapp.tests.page_logger import PageLogger

class Test(TestCase, PageLogger):
    '''
    Base class for the rest of tests.
    '''

    fixtures = ['small_db.json']

    def log_admin(self):
        self.client.login(username='admin', password='admin')

    def log_lib(self):
        self.client.login(username='lib', password='lib')

    def log_user(self):
        self.client.login(username='user', password='user')

    def test_nothing(self):
        self.assert_(True)
