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
        self.client.logout()
        self.client.login(username='admin', password='admin')

    def log_lib(self):
        ''' Logs in as librarian - some more permissions than user '''
        self.client.logout()
        self.client.login(username='lib', password='lib')

    def log_user(self):
        ''' Logs in as user '''
        self.client.logout()
        self.client.login(username='user', password='user')

    def logout(self):
        ''' Logs out '''
        self.client.logout()

    def test_nothing(self):
        self.assert_(True)

    def get_state(self, *classes):
        '''
        Desc:
            This is meant for testing sets of model instances, most likely before and after a request

        Return:
            dictionary of list of all elements of each of classes
            looks like:
            {'ClassName1' : [class_name_1_objects] , 'Class2' : [class_2_objects]}
        '''

        dict = {}
        
        # check db state before request
        for klass in classes:
            dict.update({klass.__name__ : list(klass.objects.all())})
        return dict
        

            
