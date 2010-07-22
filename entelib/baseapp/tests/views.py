# -*- coding: utf-8 -*-
from baseapp.tests.test_base import Test
from django.test import TestCase

class TestWithSmallDB(Test):
    fixtures = ['small_db.json']

class LoadDefaultConfig(TestWithSmallDB):
    pass


class ShowConfigOptions(TestWithSmallDB):
    pass


class EditConfigOption(TestWithSmallDB):
    pass


class ShowEmailLog(Test):
    pass


class ShowConfigoptions(TestWithSmallDB):
    pass


class EditConfigOption(TestWithSmallDB):
    pass


class ShowEmailLog(TestWithSmallDB):
    pass


class RequestBook(TestWithSmallDB):
    pass


class Register(TestWithSmallDB):
    pass


class Logout(TestWithSmallDB):
    ''' Test logout view '''
    def setUp(self):
        self.url = '/entelib/logout/'

    def test_not_logged_logout(self):
        self.client.logout()
        self.client.get(self.url)
        self.assertEqual(302, self.get_status_code('/entelib/'))

    def test_logout(self):
        self.client.get(self.url)
        self.assertEqual(302, self.get_status_code('/entelib/'))

    def test_logout_admin(self):
        self.log_admin()
        self.assertEqual(200, self.get_status_code('/entelib/'), "Failed to login")
        self.client.get(self.url)
        self.assertEqual(302, self.get_status_code('/entelib/'), "Unexpected access after logout")

    def test_logout_lib(self):
        self.log_lib()
        self.assertEqual(200, self.get_status_code('/entelib/'), "Failed to login")
        self.client.get(self.url)
        self.assertEqual(302, self.get_status_code('/entelib/'), "Unexpected access after logout")

    def test_logout_user(self):
        self.log_user()
        self.assertEqual(200, self.get_status_code('/entelib/'), "Failed to login")
        self.client.get(self.url)
        self.assertEqual(302, self.get_status_code('/entelib/'), "Unexpected access after logout")


class Default(TestWithSmallDB):
    pass


class MyNewReservation(TestWithSmallDB):
    pass


class ShowBooks(TestWithSmallDB):
    pass


class ShowBook(TestWithSmallDB):
    pass


class ShowBookcopy(TestWithSmallDB):
    pass


class ShowUsers(TestWithSmallDB):
    def setUp(self):
        self.url = '/entelib/users/'

    def test_annonymous_cannot_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, '/entelib/login/?next=/entelib/users/')

    def test_user_cannot_access(self):
        self.log_user()
        response = self.client.get(self.url)
        self.assertRedirects(response, '/entelib/login/?next=/entelib/users/')

    def test_librarian_can_acces(self):
        self.log_lib()
        self.assertEqual(200, self.get_status_code(self.url))

    def test_users_are_not_listed_at_first(self):
        self.log_lib()
        response = self.client.get(self.url)
        self.assertEquals(200, response.status_code)
        self.assertNotContains(response, 'superadmin')
        self.assertNotContains(response, 'Admino Domino')
        self.assertNotContains(response, 'Librariano')
        self.assertNotContains(response, 'Grzegorz')
        self.assertNotContains(response, 'No users found')
        
    def test_admins_found_by_name(self):
        self.log_lib()
        response = self.client.post(self.url, {'action' : 'Search', 'first_name' : 'admino'})
        self.assertContains(response, 'superadmin')
        self.assertContains(response, u'Admino Domino')
        self.assertNotContains(response, 'Librariano')
        self.assertNotContains(response, 'Grzegorz')

    def test_grzegorz_found_by_part_of_surname(self):
        self.log_lib()
        response = self.client.post(self.url, {'action' : 'Search', 'last_name' : 'brz'})
        self.assertNotContains(response, 'superadmin')
        self.assertNotContains(response, 'Admino Domino')
        self.assertNotContains(response, 'Librariano')
        self.assertContains(response, 'Grzegorz')

    def test_find_all(self):
        self.log_lib()
        response = self.client.post(self.url, {'action' : 'Search', })
        self.assertEquals(200, response.status_code)
        self.assertContains(response, 'superadmin')
        self.assertContains(response, 'Admino Domino')
        self.assertContains(response, 'Librariano')
        self.assertContains(response, 'Grzegorz')
        
    def test_none_found(self):
        self.log_lib()
        response = self.client.post(self.url, {'action' : 'Search', 'first_name' : 'urban' })
        self.assertEquals(200, response.status_code)
        self.assertNotContains(response, 'superadmin')
        self.assertNotContains(response, 'Admino Domino')
        self.assertNotContains(response, 'Librariano')
        self.assertNotContains(response, 'Grzegorz')
        self.assertContains(response, 'No users found')



class AddUser(TestWithSmallDB):
    pass


class ShowUser(TestWithSmallDB):
    pass


class DoEditUserProfile(TestWithSmallDB):
    pass


class EditUserProfile(TestWithSmallDB):
    pass


class ShowUserRentals(TestWithSmallDB):
    pass


class ShowMyRentals(TestWithSmallDB):
    pass


class ShowUserReservations(TestWithSmallDB):
    pass


class ShowMyReservations(TestWithSmallDB):
    pass


class ShowMyReservations(TestWithSmallDB):
    pass


class ShowReports(TestWithSmallDB):
    pass


class FindBookForUser(TestWithSmallDB):
    pass


class ReserveForUser(TestWithSmallDB):
    pass


class ShowUserReservation(TestWithSmallDB):
    pass


class Reserve(TestWithSmallDB):
    pass


class CancelAllMyReserevations(TestWithSmallDB):
    pass


class CancelAllUserResevations(TestWithSmallDB):
    pass


class LoadDefaultConfig(TestWithSmallDB):
    pass


