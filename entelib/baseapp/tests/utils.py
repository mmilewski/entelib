# -*- coding: utf-8 -*-
from entelib.baseapp.utils import pprint, remove_non_ints
from django.test import TestCase
from baseapp.utils import create_days_between
from datetime import date, timedelta

class RemoveNotIntsTest(TestCase):

    def test_remove_non_ints__empty(self):
        self.assertEquals([], remove_non_ints([]))

    def test_remove_non_ints__int(self):
        self.assertEquals([6, 8, 2, 1], remove_non_ints([6, 8, 2, 1]))

    def test_remove_non_ints__float(self):
        self.assertEquals([3, 5, 0], remove_non_ints([3.2, 5.9, 1.0/3.0]))

    def test_remove_non_ints__str(self):
        self.assertEquals([6, 8, 2, 1], remove_non_ints(['6', '  8', '2  ', '  1 ']))

    def test_remove_non_ints__dict(self):
        self.assertEquals([], remove_non_ints( [{1:2}, {}, {'a':[1,2]}] ))

    def test_remove_non_ints__list(self):
        self.assertEquals([], remove_non_ints([ [], [1,2], [7,8,9] ]))


class CreateDatesBetween(TestCase):
    def test_create_days_between__empty_range(self):
        start = date(2010, 1, 20)
        end = date(2010, 1, 19)
        self.assert_(start > end)
        self.assertEquals([], create_days_between(start, end, include_start=True,  include_end=True))
        self.assertEquals([], create_days_between(start, end, include_start=True,  include_end=False))
        self.assertEquals([], create_days_between(start, end, include_start=False, include_end=False))
        self.assertEquals([], create_days_between(start, end, include_start=False, include_end=True))
    
    def test_create_days_between__left_included(self):
        start = date(2010, 1, 20)
        end = date(2010, 1, 22)
        middle = start + timedelta(1)
        self.assert_(start < end)
        self.assertEquals([start, middle, end], create_days_between(start, end, include_start=True, include_end=True))
        self.assertEquals([start, middle],      create_days_between(start, end, include_start=True, include_end=False))
    
    def test_create_days_between__right_included(self):
        start = date(2010, 1, 20)
        end = date(2010, 1, 22)
        middle = start + timedelta(1)
        self.assert_(start < end)
        self.assertEquals([start, middle, end], create_days_between(start, end, include_start=True,  include_end=True))
        self.assertEquals([middle, end],        create_days_between(start, end, include_start=False, include_end=True))
    
    def test_create_days_between__one_day_mix_included(self):
        start = date(2010, 1, 20)
        end = date(2010, 1, 20)
        self.assert_(start <= end)
        self.assertEquals([start], create_days_between(start, end, include_start=True,  include_end=True))
        self.assertEquals([end],   create_days_between(start, end, include_start=True,  include_end=True))
        self.assertEquals([start], create_days_between(start, end, include_start=True,  include_end=False))
        self.assertEquals([start], create_days_between(start, end, include_start=False, include_end=True))
        self.assertEquals([],      create_days_between(start, end, include_start=False, include_end=False))
        
    def test_create_days_between__two_days_mixed_included(self):
        start = date(2010, 1, 20)
        end = date(2010, 1, 21)
        self.assert_(start < end)
        self.assertEquals([start,end], create_days_between(start, end, include_start=True,  include_end=True))
        self.assertEquals([start], create_days_between(start, end, include_start=True,  include_end=False))
        self.assertEquals([end], create_days_between(start, end, include_start=False, include_end=True))
        self.assertEquals([],      create_days_between(start, end, include_start=False, include_end=False))
        
