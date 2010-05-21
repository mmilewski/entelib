# -*- coding: utf-8 -*-
from django.test import TestCase
from django.conf import settings

from baseapp.config import Config
from baseapp.models import Configuration as ConfigModel


class DbConfigTest(TestCase):
    '''
    Tests for configuration stored in database and accessed via Config module.
    '''

    def setUp(self):
        self.c = Config()
        data = [
            ('mickey_mouse_creator', 'Disney'),
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
        self.c.set_str('mickey_mouse_creator', 'Walt Disney')
        self.assertEqual(unicode, type(self.c.get_str('mickey_mouse_creator')))
        self.assertEqual('Walt Disney', self.c.get_str('mickey_mouse_creator'))
        self.assertEqual(unicode, type(self.c['mickey_mouse_creator']))
        self.assertEqual('Walt Disney', self.c['mickey_mouse_creator'])

    def test_creating_string(self):
        self.c['almost_random_prefix'] = 'tralala'
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

    def test_creating_int(self):
        self.c['some_int_name'] = 123654
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

    def test_creating_bool(self):
        self.c['green_apples_exists'] = True
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

    def test_creating_list(self):
        self.c['mixed_list'] = [1, 3.1416,'hello', "world"]
        self.assertEqual(type([]), type(self.c.get_list('mixed_list')))
        self.assertEqual([1,3.1416, 'hello', "world"], self.c.get_list('mixed_list'))
