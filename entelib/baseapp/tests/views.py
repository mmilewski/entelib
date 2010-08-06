# -*- coding: utf-8 -*-
from baseapp.tests.test_base import Test
from entelib.baseapp.utils import pprint, today, tomorrow, after_days
import random
from datetime import date, timedelta
from entelib.baseapp.config import Config
from entelib.baseapp.models import Reservation, Rental, User, UserProfile, Book, BookCopy, BookRequest, Configuration, Phone, Building

class TestWithSmallDB(Test):
    '''
    A class to test views. It uses a fixture of a small but complete database dump. 
    By inheriting from Test, it inherits from django.test.TestCase and from baseapp.tests.PageLogger
    '''
    fixtures = ['small_db.json']

class LoadDefaultConfigTest(TestWithSmallDB):
    pass


class ShowConfigOptionsTest(TestWithSmallDB):
    def setUp(self):
        self.url = '/entelib/config/'
        self.log_user()

    def test_all_displayed(self):
        response = self.client.get(self.url)
        
        self.assertContains(response, 'List of configurable options')
        for c in Configuration.objects.all():
            self.assertContains(response, c.key)
        # self.assertContains(response, 'edit.png', count=Configuration.objects.filter(can_override=True).count())
        # this will fail due to many comments in html code containing 'edit.png' string



class EditConfigOptionTest(TestWithSmallDB):
    def setUp(self):
        self.url = '/entelib/config/%s/'
        self.log_user()

    def test_each_option_gets_displayed(self):
        for c in Configuration.objects.all():
            response = self.client.get(self.url % c.key)
            self.assertContains(response, c.key)

    def test_override_to_the_same_value(self):
        for c in Configuration.objects.all():
            if not c.can_override:
                continue
            response = self.client.post(self.url % c.key, {'value' : c.value})
            self.assertRedirects(response, '/entelib/config/')
            self.assertEquals(c.value, Configuration.objects.get(key=c.key).value)

#    def test_override_append_letter_to_non_ints(self):
#        for c in Configuration.objects.all():
#            if not c.can_override:
#                continue
#            if isinstance(c.value, int):
#                continue
#            response = self.client.post(self.url % c.key, {'value' : c.value + 'a'})
#            self.assertRedirects(response, '/entelib/config/')
#            self.assertEquals(c.value + 'a', Configuration.objects.get(key=c.key).value)
#
#
#            #self.assertEquals(200, response.status_code)


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
        self.log_admin()
    
    def test_one_exists(self):
        all_book_requests = BookRequest.objects.all()
        self.assertEqual(1, all_book_requests.count())

    def test_request_copy(self):
        info = 'Czemu ciagle jej nie ma?'
        book_id = 2

        before = self.get_state(BookRequest)

        response = self.client.post(self.url, {'book' : book_id, 'info' : info})

        after = self.get_state(BookRequest)

        self.assertEqual(200, response.status_code)                                     # response ok
        self.assertEquals(len(before['BookRequest']) + 1, len(after['BookRequest']))    # exactly one came in
        self.assertTemplateUsed(response, 'book_request.html')                          # correct template
        self.assertContains(response, 'Thank you')                                      # request made: thanks
        last_added_book_request = BookRequest.objects.latest(field_name='id')           # our request is last
        self.assertEqual(book_id, last_added_book_request.book.id)                      # it's for the book we wanted
        self.assertEqual(info, last_added_book_request.info)                            # and has the text we wanted

    def test_request_new_book(self):
        info = 'Scialbym jo take inne ksiomrze, kturej tu ni mocie, panocki...'
        response = self.client.post(self.url, {'book' : '0', 'info' : info})
        self.assertEqual(200, response.status_code)
        all_book_requests = BookRequest.objects.all()
        self.assertEqual(2, all_book_requests.count())
        last_added_book_request = BookRequest.objects.latest(field_name='id')
        self.assertEqual(None,last_added_book_request.book)
        self.assertEqual(info, last_added_book_request.info)

    def test_request_copy_of_not_existing_book(self):
        self.log_admin()
        before = self.get_state(BookRequest)

        response = self.client.post(self.url, {'book' : '39', 'info' : 'a taka to dacie rade zalatwic?'})

        after = self.get_state(BookRequest)

        self.assertEqual(before, after)
        # self.assertContains(response, 'Corrupted') # there are diffrent error messages
        self.assertEqual(200, response.status_code)


class RegisterTest(TestWithSmallDB):
    pass  # TODO


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

#    def prepare_random(self):
#        from entelib.baseapp.models import Book
#        self.book = random.choice(Book.objects.all())
#        self.url = self.url % self.book.id
#        self.log_user()
#        self.response = self.client.get(self.url)
#
#    def test_random_book_authors_displayed(self):
#        self.prepare_random()
#        for author in self.book.author.all():    # all authors displayed
#            self.assertContains(self.response, author.name, msg_prefix='Authors not displayed properly for book id %d' % self.book.id)
#
#    def test_random_book_categories_displayed(self):
#        self.prepare_random()
#        for category in self.book.category.all():
#            self.assertContains(self.response, category.name, msg_prefix='Categories not displayed properly for book id %d' % self.book.id)
#
#    def test_random_book_all_copies_displayed(self):
#        self.prepare_random()
#        for copy in self.book.bookcopy_set.all():
#            self.assertContains(self.response, copy.shelf_mark, msg_prefix='Categories not displayed properly for book id %d' % self.book.id)

    def test_all_books_display(self):
        for book in Book.objects.all():
            response = self.client.get(self.url % book.id)
            self.assertContains(response, book.title)  # title is displayed
            for author in book.author.all():           # all authors displayed
                self.assertContains(response, author.name, msg_prefix='Authors not displayed properly for book id %d' % book.id)
            for category in book.category.all():       # all categories displayed
                self.assertContains(response, category.name, msg_prefix='Categories not displayed properly for book id %d' % book.id)
            for copy in book.bookcopy_set.all():        # all copies displayed
                self.assertContains(response, copy.shelf_mark, msg_prefix='Categories not displayed properly for book id %d' % book.id)


class ShowBookcopyTest(TestWithSmallDB):
    def setUp(self):
        self.log_user()
        self.url = '/entelib/bookcopy/%d/'

    def assert_specific_copy_display_correct(self, copy):
        url = self.url % copy.id   # fill gap in url
        self.response = self.client.get(url)
        # test ID displayed
        self.assertContains(self.response, copy.shelf_mark, msg_prefix='ID (shelf_mark) not displayed properly for %s' % url)
        # test authors displayed
        for author in copy.book.author.all():
            self.assertContains(self.response, author.name, msg_prefix=u'Author (%s) not displayed for copy %d on %s' % (author.name, copy.id, url))
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
        copies = (BookCopy.objects.all())
        copy = copies[len(copies)*113 % len(copies)]  # pseudo-random choice from copies
        self.assert_specific_copy_display_correct(copy)
        
    def test_all_copies_display(self):
        for copy in BookCopy.objects.all():
            self.assert_specific_copy_display_correct(copy)
        
    # mmi: picture's div is now (since r322) displayed iff picture is defined for book copy.
    # def test_diffrent_users_get_the_same_page(self):
    #     import re
    #     copy = random.choice(BookCopy.objects.all())
    #     self.url = self.url % copy.id
    #     user_response = self.client.get(self.url)
    #     self.log_lib()
    #     lib_response = self.client.get(self.url)
    #     self.log_admin()
    #     admin_response = self.client.get(self.url)
    #     contents_user = re.search(r'<div class="picture">.*', ''.join(user_response.content.splitlines())).group()    # Get page contents from <div class='picture'>
    #     contents_lib = re.search(r'<div class="picture">.*', ''.join(lib_response.content.splitlines())).group()      # to the end of document.
    #     contents_admin = re.search(r'<div class="picture">.*', ''.join(admin_response.content.splitlines())).group()  # It is book copy description.
    #     self.assertEqual(contents_user, contents_lib)     # this part of page everybody should have the same
    #     self.assertEqual(contents_user, contents_admin)   # this part of page everybody should have the same

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
        self.assertContains(response, 'checked', count=1)
        self.assertNotContains(response, 'superadmin')
        self.assertNotContains(response, 'Admino Domino')
        self.assertNotContains(response, 'Librariano')
        self.assertNotContains(response, 'Grzegorz')
        self.assertNotContains(response, 'No users found')
        
    def test_admins_found_by_name(self):
        self.log_lib()
        response = self.client.post(self.url, {'action' : 'Search', 'first_name' : 'admino', 'building' : '0'})
        self.assertContains(response, 'checked', count=1)
        self.assertContains(response, 'superadmin', count=1)
        self.assertContains(response, u'Admino Domino', count=1)
        self.assertContains(response, u'admino', count=2)
        self.assertNotContains(response, 'Librariano')
        self.assertNotContains(response, 'Grzegorz')

    def test_grzegorz_found_by_part_of_surname(self):
        self.log_lib()
        response = self.client.post(self.url, {'action' : 'Search', 'last_name' : 'brz', 'building' : '0'})
        self.assertContains(response, 'checked', count=1)
        self.assertNotContains(response, 'superadmin')
        self.assertNotContains(response, 'Admino Domino')
        self.assertNotContains(response, 'Librariano')
        self.assertContains(response, 'Grzegorz', count=1)

    def test_find_all(self):
        self.log_lib()
        response = self.client.post(self.url, {'action' : 'Search', 'building' : '0', })
        self.assertEquals(200, response.status_code)
        self.assertContains(response, 'checked', count=1)
        self.assertContains(response, 'superadmin', count=1)
        self.assertContains(response, 'Admino Domino', count=1)
        self.assertContains(response, 'Librariano', count=1)
        self.assertContains(response, 'Grzegorz', count=1)
        
    def test_none_found(self):
        self.log_lib()
        response = self.client.post(self.url, {'action' : 'Search', 'first_name' : 'urban', 'building' : '0' })
        self.assertEquals(200, response.status_code)
        self.assertContains(response, 'checked', count=1)
        self.assertNotContains(response, 'superadmin')
        self.assertNotContains(response, 'Admino Domino')
        self.assertNotContains(response, 'Librariano')
        self.assertNotContains(response, 'Grzegorz')
        self.assertContains(response, 'No users found', count=1)

    def test_none_found_2(self):
        self.log_lib()
        response = self.client.post(self.url, {'action' : 'Search', 'first_name' : 'admino', 'last_name' : 'brz', 'email' : 'master-over-masters@super.net', 'building' : '0' })
        self.assertEquals(200, response.status_code)
        self.assertContains(response, 'checked', count=1)
        self.assertNotContains(response, 'superadmin')
        self.assertNotContains(response, 'Admino Domino')
        self.assertNotContains(response, 'Librariano')
        self.assertNotContains(response, 'Grzegorz')
        self.assertContains(response, 'No users found', count=1)

    def test_from_my_building_lib(self):
        self.log_lib()
        response = self.client.post(self.url, {'action' : 'Search', 'first_name' : '', 'last_name' : '', 'email' : '', 'building' : '0', 'from_my_building' : 'checked' })
        self.assertEquals(200, response.status_code)
        self.assertContains(response, 'checked', count=3)
        self.assertNotContains(response, 'superadmin')
        self.assertNotContains(response, 'Admino Domino')
        self.assertContains(response, 'Librariano')
        self.assertContains(response, 'Grzegorz')
        self.assertNotContains(response, 'No users found')

    def test_from_my_building_lib_building_given(self):
        self.log_lib()
        response = self.client.post(self.url, {'action' : 'Search', 'first_name' : '', 'last_name' : '', 'email' : '', 'building' : '2', 'from_my_building' : 'checked' })
        self.assertEquals(200, response.status_code)
        self.assertContains(response, 'checked', count=3)
        self.assertNotContains(response, 'superadmin')
        self.assertNotContains(response, 'Admino Domino')
        self.assertContains(response, 'Librariano')
        self.assertContains(response, 'Grzegorz')
        self.assertNotContains(response, 'No users found')

    def test_from_my_building_admin_building_given(self):
        self.log_admin()
        response = self.client.post(self.url, {'action' : 'Search', 'first_name' : '', 'last_name' : '', 'email' : '', 'building' : '3', 'from_my_building' : 'checked' })
        self.assertEquals(200, response.status_code)
        self.assertContains(response, 'checked', count=3)
        self.assertContains(response, 'superadmin')
        self.assertContains(response, 'Admino Domino')
        self.assertNotContains(response, 'Librariano')
        self.assertNotContains(response, 'Grzegorz')
        self.assertNotContains(response, 'No users found')


class AddUserTest(TestWithSmallDB):
    pass


class ShowUserTest(TestWithSmallDB):
    pass


class EditUserProfileTest(TestWithSmallDB):
    def setUp(self):
        self.url = '/entelib/profile/'

    def assert_display_some_important_details(self, url, user):
        response = self.client.get(url)

        self.assertContains(response, user.first_name) 
        self.assertContains(response, user.last_name) 
        self.assertContains(response, user.username) 
        self.assertContains(response, user.email) 
        for phone in user.userprofile.phone.all():
            self.assertContains(response, phone.type.name) 
            self.assertContains(response, phone.value) 

    def test_user_profiles_displayed(self):
        self.log_user()
        user = User.objects.get(username='user')
        self.assert_display_some_important_details(self.url, user)

        self.log_lib()
        user = User.objects.get(username='lib')
        self.assert_display_some_important_details(self.url, user)

        self.log_admin()
        user = User.objects.get(username='admin')
        self.assert_display_some_important_details(self.url, user)


class DoEditUserProfileTest(EditUserProfileTest):  # for view show_user
    def setUp(self):
        super(self.__class__, self).setUp()
        self.url_admin = '/entelib/users/%d/'
        self.log_admin()

    # aux

    def create_post(self, user, password, dict={}):
        ''' user is User object, password is string '''
        d0 = {
            'username' : user.username,
            'first_name' : user.first_name,
            'last_name' : user.last_name,
            'current_password' : password,
            'email' : user.email,
            'work_building' : user.userprofile.building_id,
            'phoneType0'  : '2',
            'phoneValue0' : '1',
            'phoneType1'  : '2',
            'phoneValue1' : '1',
            'phoneType2'  : '2',
            'phoneValue2' : '1',
            'phoneType3'  : '2',
            'phoneValue3' : '1',
            'phoneType4'  : '2',
            'phoneValue4' : '1',
            'password1' : '',
            'password2' : '',
        }
        d0.update(dict)
        return d0

    # assertions

    def assert_can_change_own_field(self, user, password, field, value):
        ''' user is User object, password is string 
            this works only for field of User class - not UserProfile class '''
        # new_value = 'new_value'  # could be passed as argument
        new_value = value
        
        before = self.get_state(User, UserProfile)
        
        self.client.login(username=user.username, password=password)
        dict = self.create_post(user, password, {field : new_value})

        response = self.client.post(self.url, dict)
        
        after = self.get_state(User, UserProfile)

        self.assertEquals(new_value, User.objects.get(id=user.id).__getattribute__(field))
        self.assertEquals(len(before['User']), len(after['User']))
        self.assertEquals((before['UserProfile']), (after['UserProfile']))

    def assert_cannot_change_others_field(self, user, password, other_user_id, field, value):
        ''' user is User object, password is string '''

        new_email = 'some.diffrent.address@other.server.com'
        self.client.login(username=user.username, password=password)
        dict = self.create_post(user, password, {field : value})
        
        before = self.get_state(User, UserProfile, Phone)

        response = self.client.post(self.url_admin % other_user_id, {'current_password' : password, 'email' : new_email})

        after = self.get_state(User, UserProfile, Phone)
        
        self.assertStatesEqual(before, after)
        self.assertEquals(302, response.status_code)

    def assert_can_change_someone_elses_field(self, user, password, field_name, post_variable_name, new_value, affected_user):
        ''' 
        field_name           - a string nameing a field
        new_value            - a string - field's value
        user, affected_user  - objects of User class
        
        '''

        url = self.url_admin % affected_user.id
        self.client.login(username=user.username, password=password)
        dict = self.create_post(affected_user, password, {field_name : new_value})
        
        response = self.client.post(url, dict)

        try:  # this takes care of fetching a value from field in either User object or UserProfile object.
            value_after_request = User.objects.get(id=affected_user.id).__getattribute__(field_name)
        except AttributeError:
            value_after_request = UserProfile.objects.get(user=affected_user).__getattribute__(field_name)
        self.assertEquals(new_value, value_after_request)

    # tests

    def test_user_can_change_username(self):
        user = User.objects.get(username='user')
        self.assert_can_change_own_field(user, 'user', 'username', 'Robocop')

    def test_user_can_change_email(self):
        user = User.objects.get(username='user')
        self.assert_can_change_own_field(user, 'user', 'email', 'new_email@russia.ru')

    def test_user_can_change_password(self):
        self.log_user()
        user = User.objects.get(username='user')
        new_password = 'brand_new_passwd'

        dict = self.create_post(user, 'user', {'password1' : new_password, 'password2' : new_password, })
        
        response = self.client.post(self.url, dict, follow=True)

        self.assertContains(response, 'updated')

        self.logout()
        self.client.login(username='user', password=new_password, follow=True)
        
        response = self.client.get('/entelib/', follow=True)
        self.assertContains(response, 'Logged')         # login with new password succeeded
        self.assertEquals(200, response.status_code)

    def test_user_cannot_change_others_email(self):
        user = User.objects.get(username='user')
        password = 'user'
        password = 'user'
        for victim in User.objects.all():
            self.assert_cannot_change_others_field(user, password, victim.id, 'email', 'no-darn@email.works')

    def test_admin_can_change_users_username(self):
        admin = User.objects.get(username='admin')
        passwd = 'admin'

        for user in User.objects.exclude(username='admin'):
            self.assert_can_change_someone_elses_field(admin, passwd, 'username', 'username', 'some_%d' % user.id, user)

    def test_admin_can_change_someone_elses_building(self):
        admin = User.objects.get(username='admin')
        passwd = 'admin'
        
        for building_to_change_to_id in ['1', '2']:
            for user in User.objects.all():  # exclude(username='admin'):
                dict = self.create_post(user, passwd, {'work_building' : building_to_change_to_id})
                
                response = self.client.post(self.url_admin % user.id, dict, follow=True)
                
                fetched_building = Building.objects.get(id=building_to_change_to_id)
                self.assertEquals(building_to_change_to_id, str(fetched_building.id))

                changed_building_name = Building.objects.get(id=int(building_to_change_to_id))
                self.assertContains(response, changed_building_name)
                self.assertContains(response, 'updated')  # not very universal

    def test_admin_can_change_someone_elses_phone(self):
        admin = User.objects.get(username='admin')
        passwd = 'admin'

        for new_phone_type, new_phone_value in [('1', '654 321 012'), ('2', 'smoking.skype')]:

            for phone_nr in xrange(0,5):
                for user in User.objects.all():  # exclude(username='admin'):
                    dict = self.create_post(user, passwd, 
                        {'phoneType%d'  % phone_nr : new_phone_type,
                         'phoneValue%d' % phone_nr : new_phone_value,
                        })
                    
                    response = self.client.post(self.url_admin % user.id, dict, follow=True)
                    
                    fetched_value = User.objects.get(id=user.id).userprofile.phone.all()[phone_nr].value
                    self.assert_(new_phone_value in [p.value for p in User.objects.get(id=user.id).userprofile.phone.all()])

                    self.assertContains(response, new_phone_value)
                    self.assertContains(response, 'updated')  # not very universal
            

class ShowUserRentalsTest(TestWithSmallDB):
    def setUp(self):
        self.url = '/entelib/users/%d/rentals/'
        self.log_lib()

    def test_all_users_have_all_rentals_displayed(self):
        for user in User.objects.all():
            url = self.url % user.id
            response = self.client.get(url)
            for rental in Rental.objects.filter(reservation__for_whom=user, end_date=None):
                self.assertContains(response, rental.reservation.book_copy.shelf_mark)


class ShowUserRentalsArchiveTest(TestWithSmallDB):
    def setUp(self):
        self.url = '/entelib/users/%d/rentals/archive/'
        self.log_lib()

    def test_all_users_have_all_rentals_displayed(self):
        for user in User.objects.all():
            url = self.url % user.id
            response = self.client.get(url)
            for rental in Rental.objects.filter(reservation__for_whom=user):
                self.assertContains(response, rental.reservation.book_copy.shelf_mark)


class ShowMyRentalsTest(TestWithSmallDB):
    def setUp(self):
        self.url = '/entelib/profile/rentals/'
        self.log_user()

    def test_all_rentals_displayed(self):
        user = User.objects.get(username='user')
        response = self.client.get(self.url)
        for rental in Rental.objects.filter(reservation__for_whom=user, end_date=None):
            self.assertContains(response, rental.reservation.book_copy.shelf_mark)


class ShowMyRentalsTest(TestWithSmallDB):
    def setUp(self):
        self.url = '/entelib/profile/rentals/'
        self.log_user()

    def test_all_rentals_displayed(self):
        user = User.objects.get(username='user')
        response = self.client.get(self.url)
        for rental in Rental.objects.filter(reservation__for_whom=user):
            self.assertContains(response, rental.reservation.book_copy.shelf_mark)


class ShowUserReservationsTest(TestWithSmallDB):
    def setUp(self):
        self.url = '/entelib/users/%d/reservations/'
        self.log_lib()

    def test_all_users_have_all_reservations_displayed(self):
        for user in User.objects.all():
            url = self.url % user.id
            response = self.client.get(url)
            for reservation in Reservation.objects.filter(for_whom=user, rental=None, when_cancelled=None):
                self.assertContains(response, reservation.book_copy.shelf_mark)

class ShowUserReservationsArchiveTest(TestWithSmallDB):
    def setUp(self):
        self.url = '/entelib/users/%d/reservations/archive/'
        self.log_lib()

    def test_all_users_have_all_reservations_displayed(self):
        for user in User.objects.all():
            url = self.url % user.id
            response = self.client.get(url)
            for reservation in Reservation.objects.filter(for_whom=user):
                self.assertContains(response, reservation.book_copy.shelf_mark, msg_prefix='User: %d, Reservation: %d' % (user.id, reservation.id))
         
        
class ShowMyReservationsTest(TestWithSmallDB):
    def setUp(self):
        self.url = '/entelib/profile/reservations/'
        self.log_user()

    def test_all_users_have_all_reservations_displayed(self):
        user = User.objects.get(username='user')
        response = self.client.get(self.url)
        for reservation in Reservation.objects.filter(for_whom=user, rental=None, when_cancelled=None):
            self.assertContains(response, reservation.book_copy.shelf_mark)

        
class ShowMyReservationsArchiveTest(TestWithSmallDB):
    def setUp(self):
        self.url = '/entelib/profile/reservations/'
        self.log_user()

    def test_all_users_have_all_reservations_displayed(self):
        user = User.objects.get(username='user')
        response = self.client.get(self.url)
        for reservation in Reservation.objects.filter(for_whom=user):
            self.assertContains(response, reservation.book_copy.shelf_mark)


class ShowReportsTest(TestWithSmallDB):
    pass


class FindBookForUserTest(TestWithSmallDB):
    pass


class ReserveTest(TestWithSmallDB):
    def setUp(self):
        self.url = '/entelib/bookcopy/%d/reserve/'
        self.log_user()

    # general looks

    def test_user_doesnt_have_rent_button(self):
        self.log_user()
        response = self.client.get(self.url % 2) # book copy 218237006 (Ogniem i mieczem)
        self.assertNotContains(response, "<input type='submit' name='action' value='rent'  ></td>")

    def test_admin_has_rent_button(self):
        self.log_admin()
        response = self.client.get(self.url % 2) # book copy 218237006 (Ogniem i mieczem)
        self.assertContains(response, "<input type='submit' name='action' value='rent'  ></td>")

    def test_rent_button_inactive(self):
        self.log_lib()
        url = self.url % 3  # permanently unavailable copy
        response = self.client.get(url)
        self.assertContains(response, "<td><input type='submit' name='action' value='rent'  disabled  ></td>")

    
    # assertions for rentals and reservations

    def assert_rental_made(self, book_copy_id, from_='', to=''):
        ''' Just checks if given data allows proper rental. '''
        url = self.url % book_copy_id

        # what was it like before
        rentals_before = list(Rental.objects.all())
        nr_of_rentals_before = len(rentals_before)

        # request
        response = self.client.post(url, {'action' : 'rent', 'from' : from_, 'to' : to, })
        
        # response code was 200
        self.assertEquals(200, response.status_code)
        # and rental was successfull
        self.assertContains(response, 'Rental made')
        
        # there is one more rental now
        rentals_after = list(Rental.objects.all())
        nr_of_rentals_after = len(rentals_after)
        self.assertEquals(nr_of_rentals_before + 1, nr_of_rentals_after)
        
        # nothing changed in rentals except there is one more now
        last_rental = Rental.objects.latest(field_name='id')
        self.assertEquals((rentals_before + [last_rental]).sort(), [r for r in Rental.objects.all()].sort())  # old set + newest == newset
        self.assertEquals([r for r in rentals_before], [r for r in Rental.objects.all()][:-1])                             # old set == newset - newest

        # last rental is for the copy we just rented
        self.assertEquals(book_copy_id, last_rental.reservation.book_copy.id)
        
        # last reservation is for the copy we just rented
        book_copy_id = BookCopy.objects.get(id=book_copy_id).id
        self.assertEquals(book_copy_id, Reservation.objects.latest(field_name='id').book_copy.id)         

        # last reservation is from today
        last_reservation = Reservation.objects.latest('id')
        self.assertEquals(today(), last_reservation.start_date)
        
        # last rental starts today
        self.assertEquals(last_rental.start_date.date(), today())

    def assert_rental_not_made(self, book_copy_id, from_='', to='', status_code=None):
        url = self.url % book_copy_id

        # situation before
        rentals_before = list(Rental.objects.all())
        reservations_before = list(Reservation.objects.all())

        # request
        response = self.client.post(url, {'action' : 'rent', 'from' : from_, 'to' : to, })

        # situation after
        rentals_after = list(Rental.objects.all())
        reservations_after = list(Reservation.objects.all())

        # no reservation or rental were added
        self.assertEquals(rentals_before, rentals_after)
        self.assertEquals(reservations_before, reservations_after)

        # test status code (if given)
        if status_code:
            self.assertEquals(status_code, response.status_code)

    def assert_reservation_made(self, copy_id, from_='', to=''):
        url = self.url % copy_id

        # what was it like before
        rentals_before = list(Rental.objects.all())
        reservations_before = list(Reservation.objects.all())

        # request
        response = self.client.post(url, {'action' : 'reserve', 'from' : from_, 'to' : to, })
        
        # response code was 200
        self.assertEquals(200, response.status_code)
        # and rental was successfull
        self.assertContains(response, 'Reservation active')
        
        # nothing changed in rentals
        rentals_after = list(Rental.objects.all())
        self.assertEquals([r for r in rentals_before], [r for r in Rental.objects.all()])

        # what is the last reservation
        last_reservation = Reservation.objects.latest('id')

        # last reservation is for the copy we just rented
        self.assertEquals(copy_id, last_reservation.book_copy.id)         

        # last reservation is from today or later
        self.assert_(last_reservation.start_date >= today())

        # last reservation starts at from
        if from_:
            self.assertEquals(from_, last_reservation.start_date.isoformat())
        else:
            self.assertEquals(last_reservation.start_date, today())


        # last reservations ends at to
        if to:
            self.assertEquals(to, last_reservation.end_date.isoformat())
        else:
            max_time = timedelta(Config().get_int('rental_duration'))
            self.assertEquals(last_reservation.start_date + max_time, last_reservation.end_date)
            

        # nothing changed in reservations except there is one more now
        last_reservation = Reservation.objects.latest(field_name='id')
        self.assertEquals((reservations_before + [last_reservation]).sort(), [r for r in Reservation.objects.all()].sort())   # old set + newest == newset
        self.assertEquals([r for r in reservations_before], [r for r in Reservation.objects.all()][:-1])                      # old set == newset - newest

    def assert_reservation_not_made(self, book_copy_id, from_='', to='', status_code=200):
        url = self.url % book_copy_id

        # situation before
        rentals_before = list(Rental.objects.all())
        reservations_before = list(Reservation.objects.all())

        # request
        response = self.client.post(url, {'action' : 'reserve', 'from' : from_, 'to' : to, })

        # situation after
        rentals_after = list(Rental.objects.all())
        reservations_after = list(Reservation.objects.all())

        # no reservation or rental were added
        self.assertEquals(rentals_before, rentals_after)
        self.assertEquals(reservations_before, reservations_after)

        # test status code
        self.assertEquals(status_code, response.status_code)

    
    # unit tests

    def test_annonymous_cant_reserve(self):
        self.logout()
        self.assert_reservation_not_made(0, status_code=302)
        # non existing book causes redirect, no error

        self.assert_reservation_not_made(4, status_code=302)
        # existance of a book doesn't change anything

        self.assert_reservation_not_made(4, from_=today().isoformat(), status_code=302)
        self.assert_reservation_not_made(4, from_=(today() + timedelta(1)).isoformat(), status_code=302)
        self.assert_reservation_not_made(4, from_=(today() - timedelta(1)).isoformat(), status_code=302)
        self.assert_reservation_not_made(4, from_=today(), to=today().isoformat(), status_code=302)
        self.assert_reservation_not_made(4, from_=today(), to=(today() + timedelta(1)).isoformat(), status_code=302)
        self.assert_reservation_not_made(4, from_=today(), to=(today() - timedelta(1)).isoformat(), status_code=302)
        self.assert_reservation_not_made(4, from_='marek', to='reset', status_code=302)
        # even incorrect post should cause no problems

    def test_incorrect_from(self):
        self.assert_reservation_not_made(4, from_='start date')
        # from should be a date

    def test_incorrect_to(self):
        self.assert_reservation_not_made(4, to='end date')
        # to should be a date

    def test_incorrect_from_and_to(self):
        self.assert_reservation_not_made(4, from_='blbla', to='hey-ho')
        # from and to should be dates (random strings given)

    def test_incorrect_book_copy(self):
        self.assert_reservation_not_made(0, status_code=404)
        # book copy of id 0 doesn't exist

    def test_incorrect_book_copy_fields_not_empty(self):
        self.assert_reservation_not_made(0, from_=today().isoformat(), to=today().isoformat(), status_code=404)
        # book copy of id 0 doesn't exist even if we add some post

    def test_no_from(self):
        self.assert_reservation_made(4, to=(today() + timedelta(3)).isoformat())
        # it's ok, should be rented from today

    def test_no_to(self):
        self.assert_reservation_made(4, from_=(today()+timedelta(3)).isoformat())
        # it's ok, should be rented for maximum possible time

    def test_start_date_later_than_end_date(self):
        self.assert_reservation_not_made(4, from_=(today()+timedelta(5)).isoformat(), to=(today()+timedelta(3)).isoformat())
        # cannot end before it starts

    def test_from_today(self):
        self.assert_reservation_made(4, from_=today().isoformat())
        # you sure can rent from today - for maximum time

    def test_empty_fields(self):
        self.assert_reservation_made(4)
        # why not - default start and end dates (today, today+max_rental_time)

    def test_till_today(self):
        self.assert_reservation_made(4, to=today().isoformat())
        # you can reserve for one day - you just have to return it by then end of the day

    def test_from_today_till_today(self):
        self.assert_reservation_made(4, from_=today().isoformat(), to=today().isoformat())
        # ok, just for today

    def test_admin_rents_book_copy(self):
        book_copy_id = 4
        self.log_admin()
        self.assert_rental_made(book_copy_id)

    def test_user_cant_rent(self):  # ever
        self.log_user()
        for book_copy in BookCopy.objects.all():                     # for each book copy
            self.assert_rental_not_made(book_copy.id, from_=today())    # make sure it won't be rented by user (with any post sent)
            self.assert_rental_not_made(book_copy.id, to=today(), status_code=403)
            self.assert_rental_not_made(book_copy.id, to=today()+timedelta(1), status_code=403)
            self.assert_rental_not_made(book_copy.id, to=today()-timedelta(1), status_code=403)
            self.assert_rental_not_made(book_copy.id, to=today()+timedelta(Config().get_int('rental_duration')), status_code=403)
            self.assert_rental_not_made(book_copy.id, to=today()+timedelta(Config().get_int('rental_duration')+1), status_code=403)
            self.assert_rental_not_made(book_copy.id, to=today()+timedelta(Config().get_int('rental_duration')-1), status_code=403)
            self.assert_rental_not_made(book_copy.id, from_=today(), to=today()+timedelta(Config().get_int('rental_duration')-1), status_code=403)
            self.assert_rental_not_made(book_copy.id, from_=today()-timedelta(1), to=today()+timedelta(Config().get_int('rental_duration')-1), status_code=403)
            self.assert_rental_not_made(book_copy.id, from_=today()+timedelta(1), to=today()+timedelta(Config().get_int('rental_duration')-1), status_code=403)

    def test_no_to_date(self):
        self.log_lib()
        book_copy_id = 4
        self.assert_rental_made(book_copy_id, from_=today().isoformat())
        # ok: default max rental time, from ignored
        
    def test_max_time(self):
        self.log_lib()
        book_copy_id = 4
        self.assert_rental_made(book_copy_id, to=today().isoformat())
        # ok: default max rental time
        
    def test_one_day(self):
        self.log_lib()
        book_copy_id = 4
        self.assert_rental_made(book_copy_id, to=(today() + timedelta(1)).isoformat())
        # ok: rental for one day
        
    def test_cant_rent_until_yesterday(self):
        self.log_lib()
        book_copy_id = 4
        self.assert_rental_not_made(book_copy_id, to=(today() - timedelta(1)).isoformat())
        # no: can't rent until yesterday
        
    def test_rent_for_max_time(self):
        self.log_lib()
        book_copy_id = 4
        self.assert_rental_made(book_copy_id, to=(today() + timedelta(Config().get_int('rental_duration'))).isoformat())
        # ok: max rental duration
        
    def test_one_day_too_long(self):
        self.log_lib()
        book_copy_id = 4
        self.assert_rental_not_made(book_copy_id, to=(today() + timedelta(Config().get_int('rental_duration') + 1)).isoformat())
        # no: too long
        
    def test_one_day_less_than_max(self):
        self.log_lib()
        book_copy_id = 4
        self.assert_rental_made(book_copy_id, to=(today() + timedelta(Config().get_int('rental_duration') - 1)).isoformat())
        # ok: one day less than max, from ignored
        
    def test_one_day_less_than_max_from_today(self):
        self.log_lib()
        book_copy_id = 4
        self.assert_rental_made(book_copy_id, to=(today() + timedelta(Config().get_int('rental_duration') - 1)).isoformat(), from_=today())
        # ok: one day less than max, from ignored
        
    def test_one_day_less_than_max_from_yesterday(self):
        self.log_lib()
        book_copy_id = 4
        self.assert_rental_made(book_copy_id, to=(today() + timedelta(Config().get_int('rental_duration') - 1)).isoformat(), from_=today() - timedelta(1))
        # ok: one day less than max, from ignored
        
    def test_one_day_less_than_max_from_tomorrow(self):
        self.log_lib()
        book_copy_id = 4
        self.assert_rental_made(book_copy_id, to=(today() + timedelta(Config().get_int('rental_duration') - 1)).isoformat(), from_=today() + timedelta(1))
        # ok: one day less than max, from ignored
        
    def test_one_day_too_long_from_tomorrow(self):
        self.log_lib()
        book_copy_id = 4
        self.assert_rental_not_made(book_copy_id, to=today() + timedelta(Config().get_int('rental_duration') + 1), from_=today() + timedelta(1))
        # no: too long


class ReserveForUserTest(ShowBookcopyTest, ReserveTest):
    ''' Test reserving and renting for one only user (id=1, user),
        but it saved a LOT of typing (or copying text). '''
    def setUp(self):
        self.log_lib()
        self.url = '/entelib/users/1/reservations/new/bookcopy/%d/'

    # following 3 methods are necessary - otherwise they would be inherited and would fail

    def test_user_cant_rent(self):
        self.log_user()
        for copy in BookCopy.objects.all():
            response = self.client.get(self.url % copy.id)
            self.assertEquals(302, response.status_code)

    def test_user_doesnt_have_rent_button(self):
        pass

    def test_diffrent_users_get_the_same_page(self):
        pass

    # if we find a way to make django load fixture in a method manually
    # the following could be testing all users:
    # mbr

    # test for every user (except for the one tested automatically e.g. witd id=1)
#    def test_renting_or_reserving_for_all_users(self):
#        tests = [met for met in dir(self) if met.startswith('test_')]
#        from entelib.baseapp.models import User
#        users = [u.id for u in User.objects.all() if u.id is not 1]
#        self.url_base = '/entelib/users/%d/reservations/new/bookcopy/%s/'
#        self.log_lib()
#        
#        # for every copy
#        for user in users:
#            # run all tests
#            for test in tests:
#                # LOAD FIXTURE HERE (not sure that is possible)
#                self.log_lib()
#                # prepare url
#                self.url = self.url_base % (user, '%d')
#                pprint(test)
#                self.__getattribute__(test)()


class CancelAllMyReserevationsTest(TestWithSmallDB):
    def setUp(self):
        self.log_user()
        self.url = '/entelib/profile/reservations/cancel-all/'

    def assert_nothing_happens(self, url):
        classes = [Reservation, Rental]
        # before.isoformat(i
        before = self.get_state(*classes)

        # request
        response = self.client.get(url)

        # after
        after = self.get_state(*classes)

        # nothing changed
        self.assertEquals(before['Rental'], after['Rental'])
        self.assertEquals(before['Reservation'], after['Reservation'])

        # allow more tests on response
        self.response = response

    def test_no_reservations_to_cancel(self):
        # at first there is nothing to cancel
        self.assert_nothing_happens(self.url)

        # page displayed correctly
        self.assertEquals(200, self.response.status_code)
        self.assertContains(self.response, 'Reservations cancelled')
        self.assertTemplateUsed(self.response, 'reservations_cancelled.html')

    def test_one_reservation_to_cancel(self):
        user = User.objects.get(id=4)
        copy = BookCopy.objects.get(id=4)
        Reservation(for_whom=user, book_copy=copy, who_reserved=user, start_date=today(), end_date=tomorrow()).save()

    def test_rentals_not_touched(self):
        pass  # TODO


class CancelAllUserResevationsTest(TestWithSmallDB):
    pass  #TODO



class ShowLocationTest(TestWithSmallDB):
    def setUp(self):
        self.log_user()
        loc_id = 1
        self.url = '/entelib/locations/%d/' % loc_id
        
    def test_displays(self):
        response = self.client.get(self.url)
        # page displayed correctly
        self.assertEquals(200, response.status_code)
        self.assertContains(response, 'W remoncie')    # remarks
        self.assertContains(response, 'Room 2')        # details
        self.assertContains(response, 'Maintainers')   # maintainers
        self.assertContains(response, 'admin')
        self.assertContains(response, 'lib')
        self.assertTemplateUsed(response, 'locations/one.html')
        
        
        
class ShowLocationsTest(TestWithSmallDB):
    def setUp(self):
        self.log_user()
        self.url = '/entelib/locations/'
        
    def test_displays(self):
        response = self.client.get(self.url)
        # page displayed correctly
        self.assertEquals(200, response.status_code)
        self.assertContains(response, 'Room 2')        # details
        self.assertContains(response, 'Maintainers')   # maintainers
        self.assertContains(response, 'admin')
        self.assertContains(response, 'lib')
        self.assertTemplateUsed(response, 'locations/list.html')
