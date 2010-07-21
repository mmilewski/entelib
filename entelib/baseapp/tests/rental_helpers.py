# -*- coding: utf-8 -*-
from django.test import TestCase
from baseapp.tests.page_logger import PageLogger
from baseapp.views_aux import get_rentals_for_copies
from baseapp.utils import pprint


class RentalsForCopiesTest(TestCase, PageLogger):
    '''
    Tests helpers for rental process. 
    '''

    fixtures = ['rentals_reservations.json']

    def setUp(self):
        pass

    def test_get_rentals_for_copies__nothing(self):
        ''' Test for empty ids.'''
        rentals = get_rentals_for_copies([])
        self.assertEquals(0, len(rentals))
    
    def test_get_rentals_for_copies__one(self):
        ''' Get rentals for one copy.'''
        rentals = get_rentals_for_copies([5])
        self.assertEquals(1, len(rentals))
        self.assertEquals(3, rentals[0].id)

    def test_get_rentals_for_copies__too_big_ids(self):
        ''' Test for ids, for which copies do not exist.'''
        rentals = get_rentals_for_copies([100, 300, 50])
        self.assertEquals(0, len(rentals))
        
    def test_get_rentals_for_copies__all_ids(self):
        ''' Checks if result contains correct copies' ids.'''
        rentals = get_rentals_for_copies(range(42))
        
        rentals_ids = [r.id for r in rentals]
        rentals_ids.sort()
        expected_ids = [1, 2, 3]
        self.assertEquals(expected_ids, rentals_ids)
