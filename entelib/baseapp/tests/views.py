# -*- coding: utf-8 -*-
from baseapp.tests.test_base import Test
from baseapp.utils import pprint


class TestWithSmallDB(Test):
    '''
    A class to test views. It uses a fixture of a small but complete database dump. 
    By inheriting from Test, it inherits from django.test.TestCase and from baseapp.tests.PageLogger
    '''
    fixtures = ['small_db.json']

class LoadDefaultConfigTest(TestWithSmallDB):
    pass


class ShowConfigOptionsTest(TestWithSmallDB):
    pass


class EditConfigOptionTest(TestWithSmallDB):
    pass


class ShowEmailLogTest(TestWithSmallDB):

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


class RequestBookTest(TestWithSmallDB):
    def setUp(self):
        self.url = '/entelib/requestbook/'
    
    def test_one_exists(self):
        from entelib.baseapp.models import BookRequest
        all_book_requests = BookRequest.objects.all()
        self.assertEqual(1, all_book_requests.count())

    def test_request_copy(self):
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

    def test_request_new_book(self):
        from entelib.baseapp.models import BookRequest
        self.log_user()
        info = 'Scialbym jo take inne ksiomrze, kturej tu ni mocie, panocki...'
        response = self.client.post(self.url, {'book' : '0', 'info' : info})
        self.assertEqual(200, response.status_code)
        all_book_requests = BookRequest.objects.all()
        self.assertEqual(2, all_book_requests.count())
        last_added_book_request = BookRequest.objects.latest(field_name='id')
        self.assertEqual(None,last_added_book_request.book)
        self.assertEqual(info, last_added_book_request.info)


class RegisterTest(TestWithSmallDB):
    pass


class LogoutTest(TestWithSmallDB):
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


class DefaultTest(TestWithSmallDB):
    pass


class MyNewReservationTest(TestWithSmallDB):
    pass


class ShowBooksTest(TestWithSmallDB):
    def setUp(self):
        self.url = '/entelib/books/'

    def test_get(self):
        ''' Test GET method. There should be no books listed '''
        self.log_user()
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertNotContains(response, 'Sorry')
        self.assertNotContains(response, 'Lem')

    def test_empty_fields(self):
        self.log_user()
        response = self.client.post(self.url, {'action' : 'Search', 'author' : '', 'title' : '', 'category' : '0'})
        self.assertEqual(200, response.status_code)
        self.assertNotContains(response, 'Sorry')
        self.assertContains(response, 'Ogniem i mieczem', count=1)
        self.assertContains(response, 'Mickiewicz', count=1)
        self.assertContains(response, 'robot', count=1)

    def test_author_lem(self):
        self.log_user()
        response = self.client.post(self.url, {'action' : 'Search', 'author' : 'lem', 'title' : '', 'category' : '0'})
        self.assertEqual(200, response.status_code)
        self.assertNotContains(response, 'Sorry')
        self.assertContains(response, 'Ogniem i mieczem', count=1)
        self.assertContains(response, 'Mickiewicz', count=1)
        self.assertContains(response, 'robot', count=1)

    def test_author_lem_or_ludek(self):
        self.log_user()
        response = self.client.post(self.url, {'action' : 'Search', 'author' : ' lem  ludek', 'title' : '', 'category' : '0', 'author_any' : 'any', })
        self.assertEqual(200, response.status_code)
        self.assertNotContains(response, 'Sorry')
        self.assertContains(response, 'Ogniem i mieczem', count=1)
        self.assertContains(response, 'Mickiewicz', count=1)
        self.assertContains(response, 'robot', count=1)

    def test_author_lem_and_ludek(self):
        self.log_user()
        response = self.client.post(self.url, {'action' : 'Search', 'author' : ' lem  ludek', 'title' : '', 'category' : '0', })
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Sorry')
        self.assertNotContains(response, 'Ogniem i mieczem')
        self.assertNotContains(response, 'Mickiewicz')
        self.assertNotContains(response, 'robot')

    def test_thrillers(self):
        self.log_user()
        response = self.client.post(self.url, {'action' : 'Search', 'author' : '', 'title' : '', 'category' : '4', })
        self.assertEqual(200, response.status_code)
        self.assertNotContains(response, 'Sorry')
        self.assertContains(response, 'Ogniem i mieczem', count=1)
        self.assertContains(response, 'Mickiewicz')
        self.assertNotContains(response, 'robot')

    def test_thrillers_history_horror(self):
        self.log_user()
        response = self.client.post(self.url, {'action' : 'Search', 'author' : '', 'title' : '', 'category' : [2, 4, 5], })
        self.assertEqual(200, response.status_code)
        self.assertNotContains(response, 'Sorry')
        self.assertContains(response, 'Ogniem i mieczem', count=1)
        self.assertContains(response, 'Mickiewicz')
        self.assertNotContains(response, 'robot')


class ShowBookTest(TestWithSmallDB):
    def setUp(self):
        self.url1 = '/entelib/books/1/'
        self.url2 = '/entelib/books/2/'


class ShowBookcopyTest(TestWithSmallDB):
    pass


class ShowUsersTest(TestWithSmallDB):
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


class AddUserTest(TestWithSmallDB):
    pass


class ShowUserTest(TestWithSmallDB):
    pass


class DoEditUserProfileTest(TestWithSmallDB):
    pass


class EditUserProfileTest(TestWithSmallDB):
    pass


class ShowUserRentalsTest(TestWithSmallDB):
    pass


class ShowMyRentalsTest(TestWithSmallDB):
    pass


class ShowUserReservationsTest(TestWithSmallDB):
    pass


class ShowMyReservationsTest(TestWithSmallDB):
    pass


class ShowReportsTest(TestWithSmallDB):
    pass


class FindBookForUserTest(TestWithSmallDB):
    pass


class ReserveForUserTest(TestWithSmallDB):
    pass


class ShowUserReservationTest(TestWithSmallDB):
    pass


class ReserveTest(TestWithSmallDB):
    pass


class CancelAllMyReserevationsTest(TestWithSmallDB):
    pass


class CancelAllUserResevationsTest(TestWithSmallDB):
    pass


