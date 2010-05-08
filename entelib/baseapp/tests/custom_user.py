# -*- coding: utf-8 -*-
from django.test import TestCase
from page_logger import *

from baseapp.models import CustomUser
from django.contrib.auth.models import Permission


class CustomUserTest(TestCase, PageLogger):
    '''
    Tests for Custom User info retrival and whether has_perm does it's job.
    '''

    test_permission = 'baseapp.list_users'   # this permission will be granted and then checked if user has_perm

    def setUp(self):
        '''
        Add normal user and group.
        '''
        user = CustomUser.objects.create_user('user', 'iam@frog.com', 'user')
        user.first_name, user.last_name, user.is_staff, user.is_superuser = u'Grzegorz', u'Brzęczyszczykiewicz', False, False
        user.user_permissions.add(CustomUserTest.test_permission)
        user.save()
        self.user = user

    def test_admin_exists(self):
        '''
        Test whether admin user exists in database.
        '''
        self.login()
        try:
            user = CustomUser.objects.get(username=PageLogger.username)
        except CustomUser.DoesNotExist, e:
            self.assert_(False and 'User must exist here. Something strange happend.')

    def test_shoe_size(self):
        '''
        Check if we can save and read custom user's shoe size.
        '''
        user = None
        # get user
        try:
            user = CustomUser.objects.get(username=self.user.username)
        except CustomUser.DoesNotExist, e:
            self.assert_(False and 'User must exist here. It was inserted in setUp')
        # set his shoe size
        user.shoe_size = 42
        user.save()

        # get user and read shoe size
        try:
            user = CustomUser.objects.get(username=self.user.username)
        except CustomUser.DoesNotExist, e:
            self.assert_(False and 'User must exist here. It was inserted in setUp')
        self.assertEqual(42, user.shoe_size)

    def test_has_perm(self):
        '''
        Checks if user has permission defined in CustomUser model.
        '''
        self.assert_(self.user.has_perm(CustomUserTest.test_permission))
        try:
            self.assert_(self.user.has_perm('say_hello_world_twice'))
            self.assert_(False and 'Assertion was to be raised')
        except:
            pass

    def test_has_group_permission(self):
        '''
        Checks if user has permission if he belongs to group that has it.
        '''
        pass
