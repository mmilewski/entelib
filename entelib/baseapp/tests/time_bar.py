# -*- coding: utf-8 -*-
from django.test import TestCase
from baseapp.tests.page_logger import PageLogger
from entelib.baseapp.utils import pprint
from entelib.baseapp.time_bar import TimeBar, Segment


class TimeBarSegmentTest(TestCase, PageLogger):
    '''
    Tests Segment instances' methods.
    '''

    def setUp(self):
        pass
    
    def test_if_segments_collide__disjoint(self):       
        self.assertFalse(Segment(1,1,0).collides_with(Segment(1,1,1)))
        self.assertFalse(Segment(1,1,0).collides_with(Segment(1,2,1)))
        self.assertFalse(Segment(5,6,0).collides_with(Segment(3,4,0)))
        self.assertFalse(Segment(3,4,0).collides_with(Segment(5,6,0)))

    def test_if_segments_collide__overlapping(self):
        self.assertTrue(Segment(1,2,1).collides_with(Segment(1,2,1)))
        self.assertTrue(Segment(1,9,1).collides_with(Segment(3,8,1)))
        self.assertTrue(Segment(3,8,1).collides_with(Segment(2,9,1)))
        self.assertTrue(Segment(3,6,1).collides_with(Segment(1,4,1)))

    def test_if_segments_collide__sticking(self):
        self.assertTrue(Segment(7,9,0).collides_with(Segment(1,7,0)))
        self.assertTrue(Segment(1,3,0).collides_with(Segment(3,7,0)))
        self.assertTrue(Segment(3,3,3).collides_with(Segment(3,3,3)))


    
class TimeBarStartEndWithValueTest(TestCase, PageLogger):
    '''
    Tests start_with_value and end_with_value methods.
    '''
    def setUp(self):
        self.time_bar = TimeBar(one=1)
    
    def test_start_with_value__empty(self):
        t = self.time_bar
        segments = []
        start_value = None
        
        self.assertRaises(ValueError, t.start_with_value, segments, start_value)
    
    def test_start_with_value__one_seg_value_eq(self):
        t = self.time_bar
        segments = [Segment(4,7,1)]
        start_value = 4

        result = t.start_with_value(segments, start_value)
        
        self.assertEquals(1, len(segments))
        self.assertEquals(1, len(result))
        self.assertEquals(Segment(4,7,1), result[0])

    def test_start_with_value__one_seg_value_lt(self):
        t = self.time_bar
        segments = [Segment(4,7,1)]
        start_value = 2
        
        result = t.start_with_value(segments, start_value)
        
        self.assertEquals(1, len(segments))
        self.assertEquals(2, len(result))
        self.assertEquals(Segment(2,3,1, True), result[0])
        self.assertEquals(Segment(4,7,1, False), result[1])

    def test_start_with_value__one_seg_value_gt(self):
        t = self.time_bar
        segments = [Segment(4,7,1)]
        start_value = 6

        result = t.start_with_value(segments, start_value)
        
        self.assertEquals(1, len(segments))
        self.assertEquals(1, len(result))
        self.assertEquals(Segment(6,7,1), result[0])
    
    def test_start_with_value__one_seg_value_too_big(self):
        t = self.time_bar
        segments = [Segment(4,7,1)]
        start_value = 20

        result = t.start_with_value(segments, start_value)
        
        self.assertEquals(1, len(segments))
        self.assertEquals(0, len(result))

    def test_start_with_value__many_segs_value_eq(self):
        t = self.time_bar
        segments = [Segment(4,7,1), Segment(8,10,1), Segment(15,20,1)]
        start_value = 4

        result = t.start_with_value(segments, start_value)
        
        self.assertEquals(3, len(segments))
        self.assertEquals(3, len(result))
        self.assertEquals(segments, result)

    def test_start_with_value__many_segs_value_lt(self):
        t = self.time_bar
        segments = [Segment(4,7,1), Segment(8,10,1), Segment(15,20,1)]
        start_value = 3

        result = t.start_with_value(segments, start_value)
        
        self.assertEquals(3, len(segments))
        self.assertEquals(4, len(result))
        self.assertEquals(segments, result[1:])
        self.assertEquals(Segment(3,3,1,True), result[0])

    def test_start_with_value__many_segs_value_gt_1(self):
        t = self.time_bar
        segments = [Segment(4,7,1), Segment(8,10,1), Segment(15,20,1)]
        start_value = 9

        result = t.start_with_value(segments, start_value)
        
        self.assertEquals(3, len(segments))
        self.assertEquals(2, len(result))
        self.assertEquals(Segment(9,10,1), result[0])
        self.assertEquals(Segment(15,20,1), result[1])

    def test_start_with_value__many_segs_value_gt_2(self):
        t = self.time_bar
        segments = [Segment(4,7,1), Segment(8,10,1), Segment(15,20,1)]
        start_value = 10

        result = t.start_with_value(segments, start_value)
        
        self.assertEquals(3, len(segments))
        self.assertEquals(2, len(result))
        self.assertEquals(Segment(10,10,1), result[0])
        self.assertEquals(Segment(15,20,1), result[1])

    def test_start_with_value__many_segs_value_gt_3(self):
        t = self.time_bar
        segments = [(4,7,1), (8,10,1), (15,20,1)]
        start_value = 8

        result = t.start_with_value(segments, start_value)
        
        self.assertEquals(3, len(segments))
        self.assertEquals(2, len(result))
        self.assertEquals(Segment(8,10,1), result[0])
        self.assertEquals(Segment(15,20,1), result[1])
    
    
    
    def test_end_with_value__one_seg_value_eq(self):
        t = self.time_bar
        segments = [Segment(4,7,1)]
        end_value = 7

        result = t.end_with_value(segments, end_value)
        
        self.assertEquals(1, len(segments))
        self.assertEquals(1, len(result))
        self.assertEquals(Segment(4,7,1), result[0])

    def test_end_with_value__one_seg_value_gt(self):
        t = self.time_bar
        segments = [Segment(4,7,1)]
        end_value = 17
        
        result = t.end_with_value(segments, end_value)
        
        self.assertEquals(1, len(segments))
        self.assertEquals(2, len(result))
        self.assertEquals(Segment(4,7,1), result[0])
        self.assertEquals(Segment(8,17,1,True), result[1])

    def test_end_with_value__one_seg_value_lt(self):
        t = self.time_bar
        segments = [Segment(4,7,1)]
        end_value = 6

        result = t.end_with_value(segments, end_value)
        
        self.assertEquals(1, len(segments))
        self.assertEquals(1, len(result))
        self.assertEquals(Segment(4,6,1), result[0])
    
    def test_end_with_value__one_seg_value_too_small(self):
        t = self.time_bar
        segments = [Segment(4,7,1)]
        end_value = 3

        result = t.end_with_value(segments, end_value)
        
        self.assertEquals(1, len(segments))
        self.assertEquals(0, len(result))

    def test_end_with_value__many_segs_value_eq(self):
        t = self.time_bar
        segments = [Segment(4,7,1), Segment(8,10,1), Segment(15,20,1)]
        end_value = 20

        result = t.end_with_value(segments, end_value)
        
        self.assertEquals(3, len(segments))
        self.assertEquals(3, len(result))
        self.assertEquals(segments, result)

    def test_end_with_value__many_segs_value_lt(self):
        t = self.time_bar
        segments = [Segment(4,7,1), Segment(9,10,1), Segment(15,20,1)]
        end_value = 8

        result = t.end_with_value(segments, end_value)
        
        self.assertEquals(3, len(segments))
        self.assertEquals(2, len(result))
        self.assertEquals(Segment(4,7,1), result[0])
        self.assertEquals(Segment(8,8,1,True), result[1])

    def test_end_with_value__many_segs_value_lt_1(self):
        t = self.time_bar
        segments = [Segment(4,7,1), Segment(8,10,1), Segment(15,20,1)]
        end_value = 9

        result = t.end_with_value(segments, end_value)
        
        self.assertEquals(3, len(segments))
        self.assertEquals(2, len(result))
        self.assertEquals(Segment(4,7,1), result[0])
        self.assertEquals(Segment(8,9,1), result[1])

    def test_end_with_value__many_segs_value_lt_2(self):
        t = self.time_bar
        segments = [Segment(4,7,1), Segment(8,10,1), Segment(15,20,1)]
        end_value = 5

        result = t.end_with_value(segments, end_value)
        
        self.assertEquals(3, len(segments))
        self.assertEquals(1, len(result))
        self.assertEquals(Segment(4,5,1), result[0])

    def test_end_with_value__many_segs_value_lt_3(self):
        t = self.time_bar
        segments = [Segment(4,7,1), Segment(8,10,1), Segment(15,20,1)]
        end_value = 4

        result = t.end_with_value(segments, end_value)
        
        self.assertEquals(3, len(segments))
        self.assertEquals(1, len(result))
        self.assertEquals(Segment(4,4,1), result[0])        
        
        
        
class TimeBar__Test(TestCase, PageLogger):
        
    def test_split_segments_by_depth__empty(self):
        pass
    
    def test_split_segments_by_depth__one_depth(self):
        pass
    
    def test_split_segments_by_depth__many_depths(self):
        pass
    
    
    def test_add_segment_between_each_two__empty(self):
        pass
    
    def test_add_segment_between_each_two__one(self):
        pass
    
    def test_add_segment_between_each_two__two(self):
        pass

    def test_add_segment_between_each_two__many(self):
        pass
    

    def test_divide_colliding_segments__empty(self):
        pass
    
    def test_divide_colliding_segments__one(self):
        pass
    
    def test_divide_colliding_segments__no_collisions(self):
        pass
    
    def test_divide_colliding_segments__collisions(self):
        pass
    
    