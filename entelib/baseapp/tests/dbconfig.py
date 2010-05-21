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
            ]
        for k, v in data:
            ConfigModel(key=k, value=v).save()

    def test_get_existing_key(self):
        self.assertEqual('Disney', self.c['mickey_mouse_creator'])

    def test_setting_value(self):
        self.c['almost_random_prefix'] = 'tralala'
        self.assertEqual('tralala', self.c['almost_random_prefix'])
        self.c['is_42_the_answer'] = True
        self.assertEqual(Config._true_value, self.c['is_42_the_answer'])  # when using brackets Config doesn't know value's type
        self.assertEqual(True, self.c.get_bool('is_42_the_answer'))       # so you should use get_bool() while _true_value is private
        self.assertEqual(False, not self.c.get_bool('is_42_the_answer'))

    def test_containing(self):
        self.assertTrue('most_funny_number' in self.c)
        self.assertTrue('some_true_value' in self.c)
        self.assertTrue('some_false_value' in self.c)
        self.assertFalse('this_string_is_not_in_config' in self.c)


    ''' int tests '''
    def test_get_int(self):
        self.assertEqual(8, self.c.get_int('most_funny_number'))

    def test_updating_int(self):
        self.c['most_funny_number'] = 42
        self.assertEqual(type(42), type(self.c.get_int('most_funny_number')))
        self.assertEqual(42, self.c.get_int('most_funny_number'))

    def test_creating_int(self):
        self.c['some_int_name'] = 123654
        self.assertEqual(123654, self.c.get_int('some_int_name'))


    ''' bool tests '''
    def test_get_bool(self):
        self.assertEqual(True, self.c.get_bool('some_true_value'))
        self.assertEqual(False, self.c.get_bool('some_false_value'))

    def test_updating_bool(self):
        self.c['some_bool_value'] = True
        self.assertEqual(type(True), type(self.c.get_bool('some_bool_value')))
        self.assertEqual(True, self.c.get_bool('some_bool_value'))
        self.c['some_bool_value'] = False
        self.assertEqual(type(False), type(self.c.get_bool('some_bool_value')))
        self.assertEqual(False, self.c.get_bool('some_bool_value'))

    def test_creating_bool(self):
        self.c['green_apples_exists'] = True
        self.assertEqual(type(True), type(self.c.get_bool('green_apples_exists')))
        self.assertEqual(True, self.c.get_bool('green_apples_exists'))


    ''' list tests '''
