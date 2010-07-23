#-*- coding=utf-8 -*- 
from django.test import TestCase
from baseapp.tests.page_logger import PageLogger

class Test(TestCase, PageLogger):
    '''
    Base class for the rest of tests.
    '''

    fixtures = ['small_db.json']

    def log_admin(self):
        ''' Logs in admin - with all permissions '''
        self.client.login(username='admin', password='admin')

    def log_lib(self):
        ''' Logs in as librarian - some more permissions than user '''
        self.client.login(username='lib', password='lib')

    def log_user(self):
        ''' Logs in as user '''
        self.client.login(username='user', password='user')

    def test_nothing(self):
        self.assert_(True)
