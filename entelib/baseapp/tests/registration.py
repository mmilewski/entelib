# -*- coding: utf-8 -*-
from django.test import TestCase
from views import TestWithSmallDB
from django.contrib.auth.models import User
# from baseapp.models import UserProfile
from baseapp.views import register
import test_utils as utils


class RegisterFreshNewUserTest(TestWithSmallDB):
    def setUp(self):
        self.new_user_url = '/entelib/register/newuser/'

    def test_fixture_loaded(self):
        self.assert_(User.objects.all().count() > 2)
        self.log_admin()
        self.log_user()
        self.log_lib()

    def test_fresh_user_form_displayed(self):
        self.logout()
        response = self.client.get(self.new_user_url, follow=True)
        self.assert_(utils.accessed(response))
        fields = response.context['form_content'].base_fields
        self.assert_('first_name' in fields)
        self.assert_('last_name' in fields)
        self.assert_('email' in fields)
        self.assert_('password1' in fields)
        self.assert_('password2' in fields)

    def test_fresh_new_user_registered(self):
        self.logout()
        email = 'jes.tem-n_owy@domain.com'
        first_name, last_name = 'Nowy', 'User12374hov21fiu3'
        data = { 'first_name' : first_name,
                 'last_name'  : last_name,
                 'username'   : 'nowyuser',
                 'email'      : email,
                 'password1'  : 'superpassword',
                 'password2'  : 'superpassword',
                }
        response = self.client.post(self.new_user_url, data)
        self.assert_(utils.accessed(response))
        self.assert_(utils.no_form_errors_happened(response.content))
        u = User.objects.get(email=email)
        self.assert_(u.first_name == first_name)
        self.assert_(u.last_name == last_name)
        self.assert_(u.is_active == False)
        self.assert_(u.userprofile.awaits_activation == True)


class AddNewUserTest(TestWithSmallDB):
    def setUp(self):
        self.add_user_url = '/entelib/users/add/'

    def test_fixture_loaded(self):
        self.assert_(User.objects.all().count() > 2)
        self.log_admin()
        self.log_user()
        self.log_lib()

    def test_only_admin_can_add_user(self):
        self.log_user()
        response = self.client.get(self.add_user_url, follow=True)
        self.assertFalse(utils.accessed(response))

        self.log_lib()
        response = self.client.get(self.add_user_url, follow=True)
        self.assertFalse(utils.accessed(response))

        self.log_admin()
        response = self.client.get(self.add_user_url, follow=True)
        self.assertTrue(utils.accessed(response))
        
    def test_user_form_displayed(self):
        self.log_admin()
        response = self.client.get(self.add_user_url, follow=True)
        self.assert_(utils.accessed(response))
        fields = response.context['form_content'].base_fields
        self.assert_('first_name' in fields)
        self.assert_('last_name' in fields)
        self.assert_('email' in fields)
        self.assert_('password1' in fields)
        self.assert_('password2' in fields)

    def test_new_user_registered(self):
        self.log_admin()
        email = 'jes.temowy@nsn.com'
        first_name, last_name = 'Jan', 'Nowak'
        data = { 'first_name' : first_name,
                 'last_name'  : last_name,
                 'username'   : 'janeknowak',
                 'email'      : email,
                 'password1'  : 'superpassword',
                 'password2'  : 'superpassword',
                }
        response = self.client.post(self.add_user_url, data)
        self.assert_(utils.accessed(response))
        self.assert_(utils.no_form_errors_happened(response.content))
        u = User.objects.get(email=email)
        self.assert_(u.first_name == first_name)
        self.assert_(u.last_name == last_name)
        self.assert_(u.is_active == True)
        self.assert_(u.userprofile.awaits_activation == True)
