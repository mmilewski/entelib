# -*- coding: utf-8 -*-
from entelib.baseapp.utils import pprint
from entelib.baseapp.time_bar import TimeBar, Segment
from django.test import TestCase
from baseapp.config import Config


class TimeBarSegmentTest(TestCase):
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

    
    def test_from_tuple(self):
        self.assertEquals(Segment.from_tuple((1,2,3)), Segment(1,2,3))

    def test_increment_z(self):
        # given
        t1 = Segment(1,2,3)
        t2 = Segment(1,2,3)
        t3 = Segment(1,2,3)
        t4 = Segment(1,2,3)
        t5 = Segment(1,2,3)

        # when
        t1.increment_z(0)
        t2.increment_z(1)
        t3.increment_z(2)
        t4.increment_z(10)
        t5.increment_z(-1)

        # then
        self.assertEquals(3, t1.z)
        self.assertEquals(4, t2.z)
        self.assertEquals(5, t3.z)
        self.assertEquals(13, t4.z)
        self.assertEquals(2, t5.z)


class TimeBarStartEndWithValueTest(TestCase):
    '''
    Tests start_with_value and end_with_value methods.
    '''
    def setUp(self):
        self.time_bar = TimeBar(Config(), one=1)
    
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
        
        
        
class TimeBarSegmentRelatedMethodsTest(TestCase):
    
    def setUp(self):
        self.t = TimeBar(Config(), one=1)

    def test_get_segments_depth__empty(self):
        t = self.t
        result = t.get_segments_depth([])
        self.assertEquals(0, result)

    def test_get_segments_depth__one_seg(self):
        t = self.t
        segments = [Segment(1,2,3)]
        result = t.get_segments_depth(segments)
        self.assertEquals(1, result)

    def test_get_segments_depth__many_seg_one_depth(self):
        t = self.t
        segments = [Segment(1,2,3), Segment(15,18,3), Segment(6,9,3)]
        self.assertEquals(1, t.get_segments_depth(segments))

    def test_get_segments_depth__many_seg_many_depth(self):
        t = self.t
        segments = [Segment(1,2,3), Segment(15,18,1), Segment(6,9,3), Segment(7,14,2)]
        self.assertEquals(3, t.get_segments_depth(segments))


    def test_divide_colliding_segments__empty(self):
        t = self.t
        segments = []
        result = t.divide_colliding_segments(segments)
        self.assertEquals(0, len(result))

    def test_divide_colliding_segments__one(self):
        t = self.t
        segments = [(5,10)]
        result = t.divide_colliding_segments(segments)
        self.assertEquals(1, len(result))
        self.assertEquals(Segment(5,10), result[0])

    def test_divide_colliding_segments__no_collisions(self):
        t = self.t
        # given
        segments = [Segment(1,2,0), Segment(15,18,0), Segment(6,9,0)]
        
        # when
        result = t.divide_colliding_segments(segments)
        
        # then
        self.assertEquals(3, len(result))   # nothing disappeared nor arrived
        self.assert_(Segment( 1,  2, 0, False) in result)
        self.assert_(Segment(15, 18, 0, False) in result)
        self.assert_(Segment( 6,  9, 0, False) in result)

    def test_divide_colliding_segments__collisions(self):
        t = self.t
        # given
        segments = [Segment(1,2,0), Segment(15,18,0), Segment(6,9,0), Segment(7,14,0)]
        
        # when
        result = t.divide_colliding_segments(segments)
        
        # then
        self.assertEquals(4, len(result))   # nothing disappeared nor arrived
        self.assert_(Segment( 1,  2, 0, False) in result)
        self.assert_(Segment(15, 18, 0, False) in result)
        self.assert_(Segment( 6,  9, 0, False) in result)
        self.assert_(Segment( 7, 14, 1, False) in result)


    def test_add_segment_between_each_two__empty(self):
        t = self.t
        segments = []
        result = t.add_segment_between_each_two(segments)
        self.assertEquals(0, len(result))
    
    def test_add_segment_between_each_two__one(self):
        t = self.t
        segments = [Segment(1,2,3)]
        result = t.add_segment_between_each_two(segments)
        self.assertEquals(1, len(result))

    def test_add_segment_between_each_two__two_no_gap(self):
        t = self.t
        # given
        segments = [Segment(1,2,0), Segment(3,8,0)]
        
        # when
        result = t.add_segment_between_each_two(segments)
        
        # then
        self.assertEquals(2, len(result))        # nothing changed
        self.assert_(segments[0] in result)
        self.assert_(segments[1] in result)

    def test_add_segment_between_each_two__two_gap(self):
        t = self.t
        # given
        segments = [Segment(1,2,0), Segment(4,8,0)]
        
        # when
        result = t.add_segment_between_each_two(segments)
        
        # then
        self.assertEquals(3, len(result))
        self.assert_(segments[0] in result)
        self.assert_(segments[1] in result)
        self.assert_(Segment(3,3,0,True) in result)
        

    def test_add_segment_between_each_two__many(self):
        t = self.t
        
        # given
        segments = [Segment(1,2,0), Segment(5,8,0), Segment(20,25,0)]
        
        # when
        result = t.add_segment_between_each_two(segments)
        
        # then
        self.assertEquals(5, len(result))
        self.assert_(segments[0] in result)
        self.assert_(segments[1] in result)
        self.assert_(segments[2] in result)
        self.assert_(Segment(3,4,0,True) in result)
        self.assert_(Segment(9,19,0,True) in result)


    def test_split_segments_by_depth__empty(self):
        t = self.t
        segments = []
        result = t.split_segments_by_depth(segments)
        self.assertEquals([], result)
    
    def test_split_segments_by_depth__one_depty(self):
        t = self.t
        # given
        segments = [Segment(1,2,0), Segment(5,8,0)]
        
        # when
        result = t.split_segments_by_depth(segments)
        
        # then
        self.assertEquals(1, len(result))
        self.assert_(Segment(1,2,0) in result[0])
        self.assert_(Segment(5,8,0) in result[0])
        
    def test_split_segments_by_depth__two_depth(self):
        t = self.t
        # given
        segments = [Segment(1,2,0), Segment(5,8,0), Segment(20,25,1)]
        
        # when
        result = t.split_segments_by_depth(segments)
        
        # then
        self.assertEquals(2, len(result))           # two distinct depths
        self.assert_(Segment(1,2,0) in result[0])
        self.assert_(Segment(5,8,0) in result[0])
        self.assert_(Segment(20,25,1) in result[1])
    
    def test_split_segments_by_depth__many_depths(self):
        t = self.t
        # given
        segments = [Segment(4,14,2), Segment(1,2,0), Segment(5,8,0), Segment(20,25,1), Segment(17,20,2)]
        
        # when
        result = t.split_segments_by_depth(segments)
        
        # then
        self.assertEquals(3, len(result))            # three distinct depths
        self.assert_(Segment(1,2,0) in result[0])
        self.assert_(Segment(5,8,0) in result[0])
        self.assert_(Segment(20,25,1) in result[1])
        self.assert_(Segment(4,14,2) in result[2])
        self.assert_(Segment(17,20,2) in result[2])
