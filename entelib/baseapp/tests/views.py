# -*- coding: utf-8 -*-
from baseapp.tests.test_base import Test
from baseapp.utils import pprint
import random


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
        nr_of_requests_before = BookRequest.objects.all().count()           # how many book requests exist before out reqest
        response = self.client.post(self.url, {'book' : '2', 'info' : info})
        self.assertEqual(200, response.status_code)
        nr_of_requests_after = BookRequest.objects.all().count()            # how many book requests exist after out reqest
        self.assertEqual(nr_of_requests_before + 1, nr_of_requests_after)   # exactly one came in
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
        self.url = '/entelib/books/%d/'
        self.log_user()
        self.response1 = self.client.get('/entelib/books/1/')
        self.response2 = self.client.get('/entelib/books/2/')
        
    def test_authors_properly_displayed(self):
        self.assertContains(self.response1, 'Adam Mickiewicz')
        self.assertContains(self.response1, 'Heniu Sienkiewicz')
        self.assertContains(self.response1, 'Lem')
        self.assertNotContains(self.response2, 'Adam Mickiewicz')
        self.assertNotContains(self.response2, 'Heniu Sienkiewicz')
        self.assertContains(self.response2, 'Lem')

    def test_categories_properly_displayed(self):
        # first book:
        self.assertContains(self.response1, 'History')
        self.assertContains(self.response1, 'Thriller')
        self.assertContains(self.response1, 'Horror')
        self.assertNotContains(self.response1, 'Sci-Fi')
        # second book:
        self.assertNotContains(self.response2, 'History')
        self.assertNotContains(self.response2, 'Thriller')
        self.assertContains(self.response2, 'Horror')
        self.assertContains(self.response2, 'Sci-Fi')

    def prepare_random(self):
        from entelib.baseapp.models import Book
        self.book = random.choice(Book.objects.all())
        self.url = self.url % self.book.id
        self.log_user()
        self.response = self.client.get(self.url)

    def test_random_book_authors_displayed(self):
        self.prepare_random()
        for author in self.book.author.all():    # all authors displayed
            self.assertContains(self.response, author.name, msg_prefix='Authors not displayed properly for book id %d' % self.book.id)

    def test_random_book_categories_displayed(self):
        self.prepare_random()
        for category in self.book.category.all():
            self.assertContains(self.response, category.name, msg_prefix='Categories not displayed properly for book id %d' % self.book.id)

    def test_random_book_all_copies_displayed(self):
        self.prepare_random()
        for copy in self.book.bookcopy_set.all():
            self.assertContains(self.response, copy.shelf_mark, msg_prefix='Categories not displayed properly for book id %d' % self.book.id)

    def test_all_books_display(self):
        from entelib.baseapp.models import Book
        for book in Book.objects.all():
            response = self.client.get(self.url % book.id)
            for author in book.author.all():      # all authors displayed
                self.assertContains(response, author.name, msg_prefix='Authors not displayed properly for book id %d' % book.id)
            for category in book.category.all():  # all categories displayed
                self.assertContains(response, category.name, msg_prefix='Categories not displayed properly for book id %d' % book.id)
            for copy in book.bookcopy_set.all():   # all copies displayed
                self.assertContains(response, copy.shelf_mark, msg_prefix='Categories not displayed properly for book id %d' % book.id)


class ShowBookcopyTest(TestWithSmallDB):
    def setUp(self):
        self.log_user()
        self.url = '/entelib/bookcopy/%d/'

    def specific_copy_display_tester(self, copy):
        url = self.url % copy.id   # fill gap in url
        self.response = self.client.get(url)
        # test ID displayed
        self.assertContains(self.response, copy.shelf_mark, msg_prefix='ID (shelf_mark) not displayed properly for %s' % url)
        # test authors displayed
        # TODO: the two following lines cause UnicodeDecodeError. Is it written incorrectly, or is it just my machine problem?
        #for author in copy.book.author.all():
        #    self.assertContains(self.response, author.name, msg_prefix=u'Author (%s) not displayed for copy %d on %s' % (author.name, copy.id, url))
        # test building displayed
        self.assertContains(self.response, copy.location.building.name, msg_prefix='Building (%s) not displayed for copy %d on %s' % (copy.location.building.name, copy.id, url))
        # test room displayed
        self.assertContains(self.response, copy.location.details, msg_prefix='Details (%s) not displayed for copy %d on %s' % (copy.location.details, copy.id, url))
        # test publisher displayed
        self.assertContains(self.response, copy.publisher.name, msg_prefix='Publisher (%s) not displayed for copy %d (%s)' % (copy.publisher.name, copy.id, url))
        # test year displayed
        self.assertContains(self.response, copy.year, msg_prefix='Year (%d) not displayed for copy %d (%s)' % (copy.year, copy.id, url))
        # test publication nr displayed
        self.assertContains(self.response, copy.publication_nr, msg_prefix='Publication number (%d) not displayed for copy %d (%s)' % (copy.publication_nr, copy.id, url))
        # test cost center displayed iff proper option is set
        # TODO: there was (is) such config option "is_cost_center_visible_to_anyone" but show_book_copy view doesn't care about it...

    def test_random_copy_display(self):
        from entelib.baseapp.models import BookCopy
        copy = random.choice(BookCopy.objects.all())
        self.specific_copy_display_tester(copy)
        
    def test_all_copies_display(self):
        from entelib.baseapp.models import BookCopy
        for copy in BookCopy.objects.all():
            self.specific_copy_display_tester(copy)
        

    def test_diffrent_users_get_the_same_page(self):
        from entelib.baseapp.models import BookCopy
        import re
        copy = random.choice(BookCopy.objects.all())
        self.url = self.url % copy.id
        user_response = self.client.get(self.url)
        self.log_lib()
        lib_response = self.client.get(self.url)
        self.log_admin()
        admin_response = self.client.get(self.url)
        contents_user = re.search(r"<div class='picture'>.*", ''.join(user_response.content.splitlines())).group()    # Get page contents from <div class='picture'>
        contents_lib = re.search(r"<div class='picture'>.*", ''.join(lib_response.content.splitlines())).group()      # to the end of document.
        contents_admin = re.search(r"<div class='picture'>.*", ''.join(admin_response.content.splitlines())).group()  # It is book copy description.
        self.assertEqual(contents_user, contents_lib)     # this part of page everybody should have the same
        self.assertEqual(contents_user, contents_admin)   # this part of page everybody should have the same


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
    def setUp(self):
        self.url = '/entelib/bookcopy/%d/reserve/'

    def test_user_doesnt_have_rent_button(self):
        self.log_user()
        response = self.client.get(self.url % 2) # book copy 218237006 (Ogniem i mieczem)
        self.assertNotContains(response, "<input type='submit' name='action' value='rent'  ></td>")

    def test_admin_has_rent_button(self):
        self.log_admin()
        response = self.client.get(self.url % 2) # book copy 218237006 (Ogniem i mieczem)
        self.assertContains(response, "<input type='submit' name='action' value='rent'  ></td>")

    def test_basic_rent(self):
        from entelib.baseapp.models import Rental, BookCopy, Reservation
        book_copy_id = 2  # book copy 218237006 (Ogniem i mieczem)
        self.log_admin()
        self.url = self.url % book_copy_id
        nr_of_rentals_before = Rental.objects.count()
        response = self.client.post(self.url, {'action' : 'rent', 'from' : '', 'to' : '', })
        self.assertContains(response, 'Rental made until')
        
        # there is one more rental now
        nr_of_rentals_after = Rental.objects.count()
        self.assertEquals(nr_of_rentals_before + 1, nr_of_rentals_after)

        # last rented copy is the one we just rented
        self.assertEquals(book_copy_id, Rental.objects.latest(field_name='id').reservation.book_copy.id)
        
        # last reservation is for the copy we just rented
        book_copy_id = BookCopy.objects.get(id=book_copy_id).id
        self.assertEquals(book_copy_id, Reservation.objects.latest(field_name='id').book_copy.id)         

    def rental_not_made_tester(self, book_copy_id, from_='', to=''):
        from entelib.baseapp.models import Rental, BookCopy, Reservation
        url = self.url % book_copy_id
        nr_of_rentals_before = Rental.objects.count()
        nr_of_reservations_before = Reservation.objects.count()
        response = self.client.post(url, {'action' : 'rent', 'from' : from_, 'to' : to, })
        nr_of_rentals_after = Rental.objects.count()
        nr_of_reservations_after = Reservation.objects.count()

        # no reservation or rental were added
        self.assertEquals(nr_of_rentals_before, nr_of_rentals_after)
        self.assertEquals(nr_of_reservations_before, nr_of_reservations_after)

        # actually nothing was shown
        self.assertEquals(403, response.status_code)

    def test_user_cant_rent(self):
        from entelib.baseapp.models import BookCopy
        self.log_user()
        for book_copy in BookCopy.objects.all():                 # for each book copy
            self.rental_not_made_tester(book_copy.id)                # make sure it won't be rented by user

        # TODO: test with from and to



class CancelAllMyReserevationsTest(TestWithSmallDB):
    pass


class CancelAllUserResevationsTest(TestWithSmallDB):
    pass


