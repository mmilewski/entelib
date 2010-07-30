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

    def assertStatesEqual(self, dict_a, dict_b):
        ''' Compares query sets or lists '''
        names_a = list(dict_a)
        names_b = list(dict_b)

        names_a.sort()
        names_b.sort()

        self.assertEquals(names_a, names_b)
#        print 'names:'
#        print names_a
#        print ''
        
        for name in names_a:  # or names_b
            list_a = dict_a[name]
#            print 'list_a:'
#            print list_a
            list_b = dict_b[name]
#            print 'list_b:'
#            print list_b

            self.assertEquals(len(list_a), len(list_b))

#            list_a.sort()
#            print 'list_a sorted'
#            print list_b
#            list_b.sort()
#            print 'list_b sorted'
#            print list_b
            map(lambda (i,j): self.failUnlessEqual(i,j), zip(list_a, list_b))

        
        

            
