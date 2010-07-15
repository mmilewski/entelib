# -*- coding: utf-8 -*-
from django.test import TestCase
#from django.conf import settings

from baseapp.config import Config
from baseapp.models import Configuration as ConfigModel
from django.contrib.auth.models import User


class BaseConfigTest(TestCase):
    '''
    Tests for configuration stored in database and accessed via Config module.
    Checks setting and getting keys and values in config.
    '''

    fixtures = ['active_user.json']
    
    def setUp(self):
        user = User.objects.get(pk=1)
        self.c = Config(user)
        data = [
            ('mickey_mouse_creator', 'Disney'),
            ('random_text', 'p2835ybnas12da'),
            ('most_funny_number', '8'),
            ('some_true_value', Config._true_value),
            ('some_false_value', Config._false_value),
            ('some_bool_value', Config._false_value),
            ('simple_int_list', '[1, 2, 7]'),
            ('empty_list', '[]'),
            ]
        for k, v in data:
            ConfigModel(key=k, value=v).save()

    def test_containing(self):
        ''' Checks if config contains values set up in setUp method. '''
        self.assertTrue('most_funny_number' in self.c)
        self.assertTrue('some_true_value' in self.c)
        self.assertTrue('some_false_value' in self.c)
        self.assertTrue('simple_int_list' in self.c)
        self.assertTrue('empty_list' in self.c)
        self.assertFalse('this_string_is_not_in_config' in self.c)


    ''' string tests '''
    def test_get_string(self):
        self.assertEqual('Disney', self.c['mickey_mouse_creator'])

    def test_updating_string_with_brackets(self):
        self.c['mickey_mouse_creator'] = 'Walt Disney'
        self.assertEqual(unicode, type(self.c.get_str('mickey_mouse_creator')))
        self.assertEqual('Walt Disney', self.c.get_str('mickey_mouse_creator'))

    def test_updating_string_with_setter(self):
        m_key, m_value = u'mickey_mouse_creator', u'Walt Disney'
        self.c.set_str(m_key, m_value)
        self.assertEqual(unicode, type(self.c.get_str(m_key)))
        self.assertEqual(m_value, self.c.get_str(m_key))

        r_key, r_value = u'random_text', u'sadjboqi73t2fhj'
        self.c.set_str(r_key, r_value)
        self.assertEqual(unicode, type(self.c[r_key]))
        self.assertEqual(r_value, self.c[r_key])

    def test_creating_string_with_brackets(self):
        self.c['almost_random_prefix'] = 'tralala'
        self.assertEqual('tralala', self.c['almost_random_prefix'])

    def test_creating_string_with_setter(self):
        self.c.set_str('almost_random_prefix', 'tralala')
        self.assertEqual('tralala', self.c['almost_random_prefix'])


    ''' int tests '''
    def test_get_int(self):
        self.assertEqual(8, self.c.get_int('most_funny_number'))

    def test_updating_int_with_brackets(self):
        self.c['most_funny_number'] = 42
        self.assertEqual(type(42), type(self.c.get_int('most_funny_number')))
        self.assertEqual(42, self.c.get_int('most_funny_number'))

    def test_updating_int_with_setter(self):
        self.c.set_int('most_funny_number', 42)
        self.assertEqual(type(42), type(self.c.get_int('most_funny_number')))
        self.assertEqual(42, self.c.get_int('most_funny_number'))

    def test_creating_int_with_brackets(self):
        self.c['some_int_name'] = 123654
        self.assertEqual(123654, self.c.get_int('some_int_name'))

    def test_creating_int_with_setter(self):
        self.c.set_int('some_int_name', 123654)
        self.assertEqual(123654, self.c.get_int('some_int_name'))


    ''' bool tests '''
    def test_get_bool(self):
        self.assertEqual(True, self.c.get_bool('some_true_value'))
        self.assertEqual(False, self.c.get_bool('some_false_value'))

    def test_updating_bool_with_brackets(self):
        self.c['some_bool_value'] = True
        self.assertEqual(type(True), type(self.c.get_bool('some_bool_value')))
        self.assertEqual(True, self.c.get_bool('some_bool_value'))
        #
        self.c['some_bool_value'] = False
        self.assertEqual(type(False), type(self.c.get_bool('some_bool_value')))
        self.assertEqual(False, self.c.get_bool('some_bool_value'))

    def test_updating_bool_with_setter(self):
        self.c.set_bool('some_bool_value', True)
        self.assertEqual(type(True), type(self.c.get_bool('some_bool_value')))
        self.assertEqual(True, self.c.get_bool('some_bool_value'))
        #
        self.c.set_bool('some_bool_value', False)
        self.assertEqual(type(False), type(self.c.get_bool('some_bool_value')))
        self.assertEqual(False, self.c.get_bool('some_bool_value'))

    def test_creating_bool_with_brackets(self):
        self.c['green_apples_exists'] = True
        self.assertEqual(Config._true_value, self.c['green_apples_exists'])           # when using brackets Config doesn't know value's type
        self.assertEqual(type(True), type(self.c.get_bool('green_apples_exists')))    # so you should use get_bool() while _true_value is private
        self.assertEqual(True, self.c.get_bool('green_apples_exists'))
        self.assertEqual(False, not self.c.get_bool('green_apples_exists'))

    def test_creating_bool_with_setter(self):
        self.c.set_bool('green_apples_exists', True)
        self.assertEqual(Config._true_value, self.c['green_apples_exists'])           # when using brackets Config doesn't know value's type
        self.assertEqual(type(True), type(self.c.get_bool('green_apples_exists')))    # so you should use get_bool() while _true_value is private
        self.assertEqual(True, self.c.get_bool('green_apples_exists'))
        self.assertEqual(False, not self.c.get_bool('green_apples_exists'))


    ''' list tests '''
    def test_get_list(self):
        self.assertEqual([1,2,7], self.c.get_list('simple_int_list'))
        self.assertEqual([], self.c.get_list('empty_list'))

    def test_updating_list_with_brackets(self):
        self.c['simple_int_list'] = [5, 25, 256, 20]
        self.assertEqual(type([]), type(self.c.get_list('simple_int_list')))
        self.assertEqual([5, 25, 256, 20], self.c.get_list('simple_int_list'))
        #
        self.c['simple_int_list'] = []
        self.assertEqual(type([]), type(self.c.get_list('simple_int_list')))
        self.assertEqual([], self.c.get_list('simple_int_list'))

    def test_updating_list_with_setter(self):
        self.c.set_list('simple_int_list', [5, 25, 256, 20])
        self.assertEqual(type([]), type(self.c.get_list('simple_int_list')))
        self.assertEqual([5, 25, 256, 20], self.c.get_list('simple_int_list'))
        #
        self.c.set_list('simple_int_list', [])
        self.assertEqual(type([]), type(self.c.get_list('simple_int_list')))
        self.assertEqual([], self.c.get_list('simple_int_list'))

    def test_creating_list_with_brackets(self):
        self.c['mixed_list'] = [1, 3.1416,'hello', "world"]
        self.assertEqual(type([]), type(self.c.get_list('mixed_list')))
        self.assertEqual([1,3.1416, 'hello', "world"], self.c.get_list('mixed_list'))

    def test_creating_list_with_setter(self):
        self.c.set_list('mixed_list', [1, 3.1416,'hello', "world"])
        self.assertEqual(type([]), type(self.c.get_list('mixed_list')))
        self.assertEqual([1,3.1416, 'hello', "world"], self.c.get_list('mixed_list'))


class UserConfigurationTest(TestCase):
    '''
    Checks customizing configuration. This means, if user can override value of some key,
    but also if he cannot because some options are unoverridable.
    '''

    fixtures = ['active_user.json', 'config_per_user.json']
    
    def setUp(self):
        user = User.objects.get(pk=1)
        self.c = Config(user=user)
#        data = [
#            ('mickey_mouse_creator', 'Disney'),
#            ('random_text', 'p2835ybnas12da'),
#            ('most_funny_number', '8'),
#            # ('some_true_value', Config._true_value),
#            # ('some_false_value', Config._false_value),
#            # ('some_bool_value', Config._false_value),
#            # ('simple_int_list', '[1, 2, 7]'),
#            # ('empty_list', '[]'),
#            ]
#        for k, v in data:
#            ConfigModel(key=k, value=v).save()
            
#    def test_if_user_exists(self):
#        ''' Checks if user exists - fixture was imported correctly. '''
#        try:
#            user = User.objects.get(pk=1)
#        except User.DoesNotExist:
#            self.assertEqual("User doesn't exists - fixture error?", "")

#    def test_adding_key(self):
#        ''' Checks if user can be given a new configuration key. '''
#        
#        pass
    
    def test_overriding_key_existing_in_uc(self):
        ''' Overrides value already assigned to some key, which is in UserConfiguration. '''
        key, value = 'reservation_rush', 324
        c = self.c
        c[key] = value
        self.assertEqual(value, c.get_int(key))
        
    def test_overriding_nonexisting_key(self):
        ''' Sets new value to key nonexisting in UserConfiguration, but existing in Configuration. '''
        key, value = 'more_than_override', 'blacker'
        c = self.c
        c.set_str(key, value)
        self.assertEqual(value, c.get_str(key))        
        
    def test_manipulation_parent_nonexisting_key(self):
        ''' Setting/Overriding key which does not exist in Configuration. Should rise KeyDoesNotExist exception. '''
        key = 'Im_not_there'
        c = self.c
        self.assertFalse(c.has_key(key))
        # this should fail while key not even exist and one asks for can_override (fails only if silent=False) 
        self.assertRaises(Config.KeyDoesNotExist, lambda: c.can_override(key, silent=False))
    
    def test_getting_value_from_uc(self):
        ''' Gets value for key in UserConfiguration. '''
        key, value = 'reservation_rush', 12
        c = self.c
        got_value = c.get_int(key)
        self.assertTrue(c.can_override(key))
        self.assertEqual(value, got_value)
            
    def test_getting_value_from_c(self):
        ''' Gets value whick is in Configuration, but not in UserConfiguration. '''
        key, value = 'more_than_gray', "black"
        c = self.c
        got_value = c.get_str(key)
        self.assertFalse(c.can_override(key))
        self.assertEqual(value, got_value)
                
                
    def test_check_if_can_override(self):
        ''' Checks if key can be overriden. '''
        yes_key = 'more_than_override'
        no_key = 'rental_duration'
        c = self.c
        self.assertTrue(c.can_override(yes_key))
        self.assertFalse(c.can_override(no_key))
        self.assertTrue(c.can_override(yes_key))
        self.assertFalse(c.can_override(no_key))
        
    def test_can_override_in_uc(self):
        ''' Checks if value can be overriden when key is in UserConfiguration. '''
        key, old_value, new_value = 'reservation_rush', 12, 742
        c = self.c
        c[key] = new_value
        got_value = c.get_int(key)
        self.assertTrue(c.can_override(key))
        self.assertEqual(new_value, got_value)
        self.assertNotEqual(old_value, got_value)
    
    def test_can_override_in_c(self):
        ''' Checks if value can be overriden when key is not in UserConfiguration (but is in Configuration). '''
        key, old_value, new_value = 'more_than_override', "default", "updated"
        c = self.c
        c.set_str(key, new_value)
        got_value = c.get_str(key)
        self.assertTrue(c.can_override(key))
        self.assertEqual(new_value, got_value)
        self.assertNotEqual(old_value, got_value)

    def test_exists_unless_in_uc(self):
        ''' Key lookup, when it is in Configuration, and not in UserConfiguration. '''
        key = 'more_than_gray'
        c = self.c
        self.assertTrue(c.has_key(key))
        self.assertTrue(key in c)
        
    def test_exists_if_in_uc(self):
        ''' Key lookup, when it is in UserConfiguration. '''
        key = 'reservation_rush'
        c = self.c
        self.assertTrue(c.has_key(key))
        self.assertTrue(key in c)

    def test_key_not_exists(self):
        ''' Checks if False is returned if key does not exist. '''
        key = 'hello_world'
        c = self.c
        self.assertTrue(key not in c)
        self.assertFalse(key in c)
        self.assertFalse(c.has_key(key))


    def test_set_can_override(self):
        ''' Checks if can_override property can be changed as required.'''
        c = self.c
        self.assertFalse(c.can_override('rental_duration'))
        c.set_can_override('rental_duration', True)
        self.assertTrue(c.can_override('rental_duration'))
        c.set_can_override('rental_duration', False)
        self.assertFalse(c.can_override('rental_duration'))

    def test_get_all_options(self):
        ''' Checks getting all options. '''
        options = [('more_than_gray',     'black', False),
                   ('more_than_override', 'black', True),
                   ('rental_duration',         30, False),
                   ('reservation_rush',        12, True),
                   ('turtle_is_slow',        True, False),
                   ]
        c = self.c
        # co == config_options. [ (key, config_option) ], where config_option is instance of Config.Option
        co = list(sorted(c.get_all_options().items()))
        self.assertEqual(len(options), len(co))
        
        # checks keys
        self.assertEqual(options[0][0], co[0][0])
        self.assertEqual(options[1][0], co[1][0])
        self.assertEqual(options[2][0], co[2][0])
        self.assertEqual(options[3][0], co[3][0])
        self.assertEqual(options[4][0], co[4][0])
        
        # check values
        self.assertEqual(options[0][1], c.as_str(co[0][1].value))
        self.assertEqual(options[1][1], c.as_str(co[1][1].value))
        self.assertEqual(options[2][1], c.as_int(co[2][1].value))
        self.assertEqual(options[3][1], c.as_int(co[3][1].value))
        self.assertEqual(options[4][1], c.as_bool(co[4][1].value))

        # check can_override
        self.assertEqual(options[0][2], co[0][1].can_override)
        self.assertEqual(options[1][2], co[1][1].can_override)
        self.assertEqual(options[2][2], co[2][1].can_override)
        self.assertEqual(options[3][2], co[3][1].can_override)
        self.assertEqual(options[4][2], co[4][1].can_override)
         
        
