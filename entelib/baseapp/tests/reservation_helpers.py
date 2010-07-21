# -*- coding: utf-8 -*-
from django.test import TestCase
from baseapp.tests.page_logger import PageLogger
from baseapp.views_aux import get_reservations_for_copies
from baseapp.utils import pprint


class ReservationsForCopiesTest(TestCase, PageLogger):
    '''
    Tests of editing user's profile.
    '''

    fixtures = ['rentals_reservations.json']

    def setUp(self):
        pass

    def test_get_rentals_for_copies__nothing(self):
        ''' Test for empty ids.'''
        rsvs = get_reservations_for_copies([])
        self.assertEquals(0, len(rsvs))
    
    def test_get_rentals_for_copies__one(self):
        ''' Get rentals for one copy.'''
        rsvs = get_reservations_for_copies([4])
        self.assertEquals(0, len(rsvs))
        
    def test_get_rentals_for_copies__one_2(self):
        rsvs = get_reservations_for_copies([2])
        self.assertEquals(1, len(rsvs))
        self.assertEquals(2, rsvs[0].id)

    def test_get_rentals_for_copies__too_big_ids(self):
        ''' Test for ids, for which copies do not exist.'''
        rsvs = get_reservations_for_copies([100, 300, 50])
        self.assertEquals(0, len(rsvs))
        
    def test_get_rentals_for_copies__all_ids(self):
        ''' Checks if result contains correct copies' ids.'''
        rsvs = get_reservations_for_copies(range(42))
        
        rsvs_ids = [r.id for r in rsvs]
        rsvs_ids.sort()
        expected_ids = [2, 4]
        self.assertEquals(expected_ids, rsvs_ids)
