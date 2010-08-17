# -*- coding: utf-8 -*-
from django.test import TestCase
#from django.conf import settings

#from baseapp.config import Config
from baseapp.models import Phone, PhoneType, UserProfile
from baseapp.forms import ProfileEditForm, ProfileEditChoiceList
from django.contrib.auth.models import User
from baseapp.tests.page_logger import PageLogger
from entelib.dbconfigfiller import fill_config
from copy import copy
from baseapp.config import Config
from test_base import Test

# class LoadingProfilePage(TestCase, PageLogger):
class LoadingProfilePage(Test):
    '''
    Checks if related pages are displaying properly.
    '''
    # fixtures = ['user_with_complete_profile.json', 'small_db-configuration.json']
    fixtures = ['small_db.json', 'small_db-configuration.json', 'small_db-groups.json', ]
    
    
    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.config = Config(self.user)
        # self.config = fill_config()
    
    def test_loading_my_profile_page(self):
        ''' Test displaying user's profile. '''
        # self.login()
        self.log_user()
        response = self.client.get('/entelib/profile/', {})
        
        self.assertEqual(200, response.status_code)
        self.assertNotContains(response, 'Forbidden')
        self.assertTemplateUsed(response, 'profile.html')
        self.assertTemplateUsed(response, 'user.html')

#    def test_visible_in_menu(self):
#        ''' Link is visible in menu.
#        
#        Menu nie wyświetla się ze względu na nieprzypisane uprawnienia.
#        '''
#        self.login()
#        response = self.client.get('/entelib/profile/', {})
#
#        link_name = u'My profile'
#        self.assertContains(response, link_name)
        

# class ProfileEditFormTest(TestCase, PageLogger):
class ProfileEditFormTest(Test):
    '''
    Tests of editing user's profile.
    '''

    # fixtures = ['user_with_complete_profile.json']
    
    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.config = Config(self.user)
        # self.config = fill_config()
        self.form = ProfileEditForm(self.user) 
        
    def test_building_choice_list(self):
        ''' Checks if list of buildings is correct.'''
        form_buildings = ProfileEditChoiceList.buildings()

        self.assertEquals(3, len(form_buildings))
        self.assertEquals( (0, u'--- not specified ---'), form_buildings[0])
        self.assertEquals( (2, u'Building A'),            form_buildings[1])
        # self.assertEquals( (1, u'Skyscraper'),            form_buildings[2])
        self.assertEquals( (1, u'Building B'),            form_buildings[2])
        
    def test_phone_types_choice_list(self):
        ''' Checks if list of buildings is correct.'''
        form_phone_types = ProfileEditChoiceList.phone_types()

        self.assertEquals(2, len(form_phone_types))
        self.assertEquals( (1, u'Mobile'), form_phone_types[0])
        self.assertEquals( (2, u'Skype'),  form_phone_types[1])


    def test_clean_phone_type(self):
        ''' Test cleaning data of phones.'''
        # given
        ptype_prefix = ProfileEditForm.phone_type_prefix
        pvalue_prefix = ProfileEditForm.phone_value_prefix
        cleaned_data = { ptype_prefix+'0'  : '1',
                         pvalue_prefix+'0' : u'100-200-300',
                         ptype_prefix+'1'  : 5,
                         pvalue_prefix+'2' : u'eugeniusz',
                        }
        
        # when
        result = self.form.get_cleaned_phones(cleaned_data)
        
        # then
        self.assertEquals(1,              result[ptype_prefix +'0'])
        self.assertEquals(5,              result[ptype_prefix +'1'])
        self.assertEquals(u'100-200-300', result[pvalue_prefix+'0'])
        self.assertEquals(u'eugeniusz',   result[pvalue_prefix+'2'])
        
    def test_transform_cleaned_phones_to_list_of_phones(self):
        ''' Tests transforming data: dict ~~> list.'''
        # given
        ptype_prefix = ProfileEditForm.phone_type_prefix
        pvalue_prefix = ProfileEditForm.phone_value_prefix
        type0, value0 = ptype_prefix+'0', pvalue_prefix+'0' 
        type1, value2 = ptype_prefix+'1', pvalue_prefix+'2'
        type5, value5 = ptype_prefix+'5', pvalue_prefix+'5'
        cleaned_phones = { type0: 1, value0: u'100-200-300',    # ok
                           type1: 5, value2: u'eugeniusz',      # mismatch
                           type5: 3, value5: u'     ' ,         # shouldn't be in result
                           }
        
        # when
        result = self.form.transform_cleaned_phones_to_list_of_phones(cleaned_phones)
        
        # then
        self.assertEquals(1, len(result))
        self.assertTrue((cleaned_phones[type0], cleaned_phones[value0]) in result)

    def test_extract_phones_to_add__nothing(self):
        ''' Testing extracting when there is nothing to be added.'''
        # given
        user_phones = Phone.objects.all()        # see fixture for details
        sent_phones = [ (1, u'100-200-300') ]
        
        # when
        result = self.form.extract_phones_to_add(user_phones, sent_phones)
        
        # then
        self.assertEquals(1, len(result))
    
    def test_extract_phones_to_add__something(self):
        ''' Testing extracting when something should be added.'''
        # given
        user_phones = Phone.objects.all()        # see fixture for details
        sent_phones = [ (2, u'mniszek'), (5, u'aabb') ]
        
        # when
        result = self.form.extract_phones_to_add(user_phones, sent_phones)
        
        # then
        self.assertEquals(2, len(result))
        
        self.assertEquals(2, result[0][0])
        self.assertEquals(u'mniszek', result[0][1])

        self.assertEquals(5, result[1][0])
        self.assertEquals(u'aabb', result[1][1])

    def test_extract_phones_to_remove__nothing(self):
        ''' Testing extracting when there is nothing to be removed.'''
        # given
        user_phones = self.user.get_profile().phone.all()        # see fixture for details
        sent_phones = [ (1, u'100-200-300') ]

        # when
        result = self.form.extract_phones_to_remove(user_phones, sent_phones)

        # then
        self.assertEquals(2, len(result))
    
    def test_extract_phones_to_remove__something(self):
        ''' Testing extracting when something should be added.'''
        # given
        user_phones = self.user.get_profile().phone.all()
        sent_phones = [ (2, u'mniszek') ]        # one to remove & one to add
        
        # when
        result = self.form.extract_phones_to_remove(user_phones, sent_phones)
        
        # then
        self.assertEquals(2, len(result))
        
        self.assertEquals(1, result[0][0])
        # self.assertEquals(u'100-200-300', result[0][1])
        self.assertEquals(u'432-765-098', result[0][1])
        
    def test_add_phones_to_profile(self):
        ''' Tests adding phone to profile.'''
        # given
        phones_to_add = [ (2, u'sroczka'), (1, '500-400-500') ]
                
        # when
        phones_in_profile_before_add = copy(self.user.get_profile().phone.all())
        self.form.add_phones_to_profile(phones_to_add)
        phones_in_profile_after_add = self.user.get_profile().phone.all()
        
        # then
        self.assertEquals(2, len(phones_in_profile_before_add)) 
        self.assertEquals(4, len(phones_in_profile_after_add))
        
    def test_remove_phones_from_profile__type_mismatch(self):
        ''' Removing when type mismatches -- nothing should be removed.'''
        # given
        phones_to_remove = [ (2, u'100-200-300') ]
        
        # when
        phones_in_profile_before_remove = copy(self.user.get_profile().phone.all())
        self.form.remove_phones_from_profile(phones_to_remove)
        phones_in_profile_after_remove = self.user.get_profile().phone.all()
        
        # then
        self.assertEquals(2, len(phones_in_profile_before_remove))
        self.assertEquals(2, len(phones_in_profile_after_remove))

        
    def test_remove_phones_from_profile__value_mismatch(self):
        ''' Removing when value mismatches -- nothing should be removed.'''
        # given
        phones_to_remove = [ (1, u'100-222-300') ]
        
        # when
        phones_in_profile_before_remove = copy(self.user.get_profile().phone.all())
        self.form.remove_phones_from_profile(phones_to_remove)
        phones_in_profile_after_remove = self.user.get_profile().phone.all()
        
        # then
        self.assertEquals(2, len(phones_in_profile_before_remove))
        self.assertEquals(2, len(phones_in_profile_after_remove))
        
    def test_remove_phones_from_profile__match(self):
        ''' Removing when type & value matches -- phone should be removed.'''
        # given
        phones_to_remove = [ (1, u'100-200-300') ]
        
        # when
        phones_in_profile_before_remove = copy(self.user.get_profile().phone.all())
        self.form.remove_phones_from_profile(phones_to_remove)
        phones_in_profile_after_remove = self.user.get_profile().phone.all()
        
        # then
        self.assertEquals(2, len(phones_in_profile_before_remove))
        self.assertEquals(2, len(phones_in_profile_after_remove))




