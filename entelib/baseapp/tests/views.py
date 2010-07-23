# -*- coding: utf-8 -*-
from baseapp.tests.test_base import Test
from baseapp.utils import pprint


class TestWithSmallDB(Test):
    '''
    A class to test views. It uses a fixture of a small but complete database dump. 
    By inheriting from Test, it inherits from django.test.TestCase and from baseapp.tests.PageLogger
    '''
    fixtures = ['small_db.json']

class LoadDefaultConfig(TestWithSmallDB):
    pass


class ShowConfigOptions(TestWithSmallDB):
    pass


class EditConfigOption(TestWithSmallDB):
    pass


class ShowConfigoptions(TestWithSmallDB):
    pass


class EditConfigOption(TestWithSmallDB):
    pass


class ShowEmailLog(TestWithSmallDB):

    def setUp(self):
        self.url = '/entelib/emaillog/'

    def test_user_has_no_access(self):
        self.log_user()
        self.assertRedirects(self.client.get(self.url), '/entelib/login/?next=' + self.url)

    def test_access(self):
        self.log_admin()
        self.assertEquals(200, self.get_status_code(self.url))

    def test_there_are_two_logged_emails(self):
        ''' One rental, and one reservation made '''
        self.log_admin()
        response = self.client.get(self.url)
        self.assertContains(response, 'Welcome!', count=2)
        self.assertContains(response, 'You have reserved', count=1)
        self.assertContains(response, 'You have rented', count=1)


class RequestBook(TestWithSmallDB):
    def setUp(self):
        self.url = '/entelib/requestbook/'
    
    def test_one_exists(self):
        from entelib.baseapp.models import BookRequest
        all_book_requests = BookRequest.objects.all()
        self.assertEqual(1, all_book_requests.count())

    def test_add_request(self):
        from entelib.baseapp.models import BookRequest
        self.log_user()
        info = 'Czemu ciagle jej nie ma???'
        response = self.client.post(self.url, {'book' : '2', 'info' : info})
        self.assertEqual(200, response.status_code)
        all_book_requests = BookRequest.objects.all()
        self.assertEqual(2, all_book_requests.count())
        last_added_book_request = BookRequest.objects.latest(field_name='id')
        self.assertEqual(2,last_added_book_request.book.id)
        self.assertEqual(info, last_added_book_request.info)




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
        self.assertContains(response, 'superadmin', count=1)
        self.assertContains(response, u'Admino Domino', count=1)
        self.assertContains(response, u'admino', count=2)
        self.assertNotContains(response, 'Librariano')
        self.assertNotContains(response, 'Grzegorz')

    def test_grzegorz_found_by_part_of_surname(self):
        self.log_lib()
        response = self.client.post(self.url, {'action' : 'Search', 'last_name' : 'brz'})
        self.assertNotContains(response, 'superadmin')
        self.assertNotContains(response, 'Admino Domino')
        self.assertNotContains(response, 'Librariano')
        self.assertContains(response, 'Grzegorz', count=1)

    def test_find_all(self):
        self.log_lib()
        response = self.client.post(self.url, {'action' : 'Search', })
        self.assertEquals(200, response.status_code)
        self.assertContains(response, 'superadmin', count=1)
        self.assertContains(response, 'Admino Domino', count=1)
        self.assertContains(response, 'Librariano', count=1)
        self.assertContains(response, 'Grzegorz', count=1)
        
    def test_none_found(self):
        self.log_lib()
        response = self.client.post(self.url, {'action' : 'Search', 'first_name' : 'urban' })
        self.assertEquals(200, response.status_code)
        self.assertNotContains(response, 'superadmin')
        self.assertNotContains(response, 'Admino Domino')
        self.assertNotContains(response, 'Librariano')
        self.assertNotContains(response, 'Grzegorz')
        self.assertContains(response, 'No users found', count=1)

    def test_none_found_2(self):
        self.log_lib()
        response = self.client.post(self.url, {'action' : 'Search', 'first_name' : 'admino', 'last_name' : 'brz', 'email' : 'master-over-masters@super.net' })
        self.assertEquals(200, response.status_code)
        self.assertNotContains(response, 'superadmin')
        self.assertNotContains(response, 'Admino Domino')
        self.assertNotContains(response, 'Librariano')
        self.assertNotContains(response, 'Grzegorz')
        self.assertContains(response, 'No users found', count=1)




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


