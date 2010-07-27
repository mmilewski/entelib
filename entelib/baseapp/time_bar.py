# -*- coding: utf-8 -*-
import random
from copy import copy
from baseapp.models import Reservation, BookCopy
from baseapp.views_aux import Q_reservation_active
from datetime import date, timedelta
from baseapp.config import Config
from fractions import gcd
from django.db.models.query_utils import Q

try:
    from baseapp.utils import pprint
except:
    from pprint import pprint


class Segment(object):
    
    def __init__(self, start, end, z=0, is_available=False):
        self.start = start
        self.end = end
        self.z = z                         # z-plane
        self.is_available = is_available   # as default Segment instance is unavailable (not rentable or sth)
    
    @classmethod
    def from_tuple(cls, tuple):
        ''' Creates instance from tuple. It may be done to work with iterable, but is not needed now.'''
        assert len(tuple) >= 2
        if len(tuple) == 2:
            return cls(tuple[0], tuple[1])
        else:
            return cls(tuple[0], tuple[1], tuple[2])
    
    def __eq__(self, other):
        return self.start == other.start and \
               self.end  == other.end and \
               self.z == other.z and \
               self.is_available == other.is_available
    
    def __repr__(self):
        return unicode(self)
    
    def __unicode__(self):
        avail_flag = 'T' if self.is_available else 'F'
        return u'Segment(%s, %s, %s, %s)' % (self.start, self.end, self.z, avail_flag)
    
    def get_html_str(self):
        ''' 
        Returns string for displaying in html. __unicode__ is not used, because 
        it returns the simplest representation of Segment -- very useful in test.
        '''
        avail_flag = 'T' if self.is_available else 'F'
        rentable_caption = 'rentable' if self.is_available else 'not rentable'
#        return u'(%s, %s, %s, %s)' % (self.start, self.end, self.z, avail_flag)
#        return u'(%s, %s)' % (self.start, self.end)
        return u'(%s, %s) %s' % (self.start, self.end, rentable_caption)
    
    def increment_z(self, by_value=1):
        ''' Increases self.z by given value.'''
        self.z += by_value
    
    def check_invariant(self):
        ''' This should always be True. '''
        if self.start > self.end:
            return False
        if self.z < 0:
            return False
        return True
    
    def collides_with(self, other):
        ''' 
        Returns True iff self collides with other.
        
        Args:
            other -- Segment instance
            
        Note: (_,5,_) collides with (5,_,_)
        '''
        assert self.check_invariant()
        assert other.check_invariant()
        if self.z != other.z:
            return False
        if other.end < self.start or self.end < other.start:   #  |----|       |----| 
            return False
        if other.end == self.start or self.end == other.start: #  |----||----|
            return True
        if self.start <= other.start <= self.end:              # a     |--------|
            return True                                        # b         |--------
        if other.start <= self.start <= other.end:             # a      |--------
            return True                                        # b   |-----|
        if self.start <= other.end <= self.end:                # a     |--------|
            return True                                        # b   ------|
        if other.start <= self.end <= other.end:               # a     |--------
            return True                                        # b         | ------|
        
        assert False, 'unexpected case'
        
    def collides_with_list(self, haystack):
        ''' 
        Checks if self collides with at least one of segments in haystack.
        
        Args:
            haystack -- list of Segment objects
        
        Returns:
            True or False respectively.
        '''
        assert self.check_invariant()
        
        for hay in haystack:
            if self.collides_with(hay):
                return True
        return False



class TimeBar(object):
    
    def __init__(self, one=1):
        '''
        Args:
            one -- smallest portion of data. Like 'one day' or '1'. This may be useful when 
                   you want to test using ints and later use dates instead.
        '''
        self.one = one

    def get_segments_depth(self, segments):
        ''' 
        Returns number of unique z-planes for given segments. 
    
        Args:
            segments -- list of Segment objects
        '''
        return len(set( [s.z for s in segments] ))

    def _assure_segment(self, segment):
        ''' 
        Returns new instance of Segment.
        Args:
            segment -- tuple or Segment instance.
        '''
        if isinstance(segment, Segment):
            return copy(segment)
        if isinstance(segment, tuple):
            return Segment.from_tuple(segment)
        assert False, 'unknown type'

        
        
    def divide_colliding_segments(self, segments, shuffle=False):
        ''' 
        Divides segments into multiple planes. So this function returns the same segments 
        but with additional coordinate - like z-plane.
        
        Args:
            segments -- list Segmant objects or 2-tuples. About each 2-tuple you can think as (start, end).
            shuffle -- if True then segments will be shuffled before use, so algorithm will be randomized.
            
        Returns:
            list of Segment objects. Result is not sorted.
        '''
        segments_left = [self._assure_segment(s) for s in segments]
        if len(segments_left) < 2:
            return segments_left
        
        max_iterations = 15                     # more then this number of iteration means an error probably
        if shuffle:
            random.shuffle(segments_left)
        result = []                             # list of 3-tuples
        iterations = 0
        while segments_left:                    # O(n*k), n - #items; k - #iterations
            iterations += 1
            if iterations > max_iterations:                
                break
            # remove noncolliding segments
            colliding_segments = list(segments_left)
            for seg in segments_left:
                if not seg.collides_with_list(result):
                    result.append(seg)
                    colliding_segments.remove(seg)
            # increase z-plane of other segments
            segments_left = colliding_segments
            for seg in segments_left:
                seg.increment_z()
        
        # check result
        assert len(result) == len(segments)
        for seg in result:
            tmp_result = list(result)
            tmp_result.remove(seg)         # seg collides with seg, so it should be removed before assert
            assert not seg.collides_with_list(tmp_result)
        
        return result
        
        
    def add_segment_between_each_two(self, segments):
        '''
        Between each two segments adds additional segment.
        
        Args:
            segments -- list of Segment objects. All must have the same z-value
        '''
        if len(segments) < 2:
            return segments
        
        modified_segs = []
        segs_count = len(segments)
        
        for i in range(segs_count-1):
            assert segments[i].z == segments[i+1].z
            old_seg = segments[i]
            modified_segs.append(old_seg)
            should_add = False
            if isinstance(segments[i+1].start, date) and isinstance(segments[i].end, date):
                should_add = (segments[i+1].start - segments[i].end).days > 1
            else:
                should_add =  segments[i+1].start - segments[i].end > 1
            if should_add:
                new_seg = Segment(old_seg.end + self.one, segments[i+1].start - self.one , old_seg.z)
                new_seg.is_available = True
                modified_segs.append(new_seg)
        modified_segs.append(segments[-1])
        return modified_segs
        
        
    def split_segments_by_depth(self, segments, sort=True):
        '''
        Splits segments by z coord. Returns list of lists, one for each group.
        If sort is True then each group will be sorted.
        '''
        depth = self.get_segments_depth(segments)
        segments_by_depth = []              # list of depth lists
        # prepare list of empty lists
        for i in range(depth): #@UnusedVariable
            segments_by_depth.append([])
        # split segments
        for segment in segments:
            segments_by_depth[segment.z].append(segment)
        # sort each group (lex sort)
        if sort:
            for group in segments_by_depth:
                cmp_by_start = lambda a,b: 0 if a.start == b.start else ( -1 if a.start < b.start else 1 ) 
                group.sort(cmp=cmp_by_start)
        return segments_by_depth
    
    
    def start_with_value(self, segments, start_value):
        ''' 
        Adds segment at the begging of group (list of segments). May return shallow copy. 
        
        Args:
            segments -- list of at least one segment (which is instance of Segment).
                        should be sorted asc by 'start' field.
            start_value -- value from which you want to start segments.
        
        Returns:
            If segments is empty, then ValueError is raised.
            If segments start with segment which start is eq start_value, then segments list is returned.
            If segments start with segment which start value is lt start_value, then segments is stripped to start_value. 
            Else returns list of segments with prepended segment with start = start_value, 
            and end set to start of first segment.
        '''
        if not segments:
            raise ValueError('segments must not be empty. start_value was: ' + repr(start_value))
        result = []
        for seg in segments:
            seg = self._assure_segment(seg)
            if (start_value <= seg.start) or (seg.start <= start_value <= seg.end):
                result.append(seg)

        # what about first element? Needs inserting or shrinking?        
        if result:
            if result[0].start > start_value:      #      |-------|------
                new_seg = copy(result[0])          #   ^
                new_seg.end = result[0].start - self.one
                new_seg.start = start_value
                new_seg.is_available = True
                result.insert(0, new_seg)
            elif result[0].start < start_value:    #    |---------|------
                result[0].start = start_value      #        ^
        return result
    
    def end_with_value(self, segments, end_value):
        '''
        Works similar to start_with_value.
        '''
        if not segments:
            raise ValueError('segments must not be empty. end_value was: ' + repr(end_value))
        result = []
        for seg in segments:
            seg = self._assure_segment(seg)
            if (end_value >= seg.end) or (seg.start <= end_value <= seg.end):
                result.append(seg)
        
        # what about last element?
        if result:
            if result[-1].end < end_value:         #  -----|-------|
                new_seg = copy(result[-1])         #                    ^
                new_seg.start = result[-1].end + self.one
                new_seg.end = end_value
                new_seg.is_available = True
                result.append(new_seg)
            elif result[-1].end > end_value:    #  |------|-------|
                result[-1].end = end_value      #             ^
        return result
    
    
    def get_width_of_group(self, group):
        '''
        Returns width of group, which means total number of units.
        i.e. width of date range 2010-07-01, 2010-07-10 is 10 (ten days).
        
        Args:
            group -- list of Segment instances.
            
        Returns:
            If group is empty, then returns -1
        '''
        if not len(group):
            return -1
        if isinstance(group[-1].end, date) and isinstance(group[0].start, date):
            group_width = (group[-1].end - group[0].start).days + 1
        else:
            group_width = (group[-1].end - group[0].start) + 1
        return group_width
    
    
    def get_html_for_scale(self, group):
        '''
        Returns html for scale (podziałka).
        
        Args:
            group -- group of segments (list of Segment instances).
            
        Raises:
            If group is empty, then raises ValueError
        '''
        if not group:
            raise ValueError('Given group is empty: %s' % (repr(group)))
        html = '<div class="scaleWrapper">'
        width = self.get_width_of_group(group)
        the_gcd = self.gcd_for_group(group)
        for i in range(width / the_gcd):
            title = 'one day' if the_gcd == 1 else '%d days' % the_gcd
            html += '<div class="scale_part" style="width: %.3f%%" title="%s">' % (100.0 * the_gcd / width, title)
            html += '</div>'
        html += '</div>'
        return html
        
        
    def gcd_for_group(self, group):
        '''
        Return greates common divisior for lengths of segments in group.
        
        If group is empty, raises ValueError.
        '''
        if not group:
            raise ValueError('Cannot get gcd for empty group') 
        if isinstance(group[0].end, date) and isinstance(group[0].start, date):
            cur_gcd = (group[0].end - group[0].start).days + 1
            for seg in group:
                cur_gcd = gcd(cur_gcd, (seg.end - seg.start).days + 1)
                if cur_gcd < 2:
                    return cur_gcd
            return cur_gcd
        else:
            cur_gcd = (group[0].end - group[0].start) + 1
            for seg in group:
                cur_gcd = gcd(cur_gcd, (seg.end - seg.start) + 1)
                if cur_gcd < 2:
                    return cur_gcd
            return cur_gcd
        
        
    def get_html_for_segments(self, grouped_segments):
        '''
        Returns html for given groups of segments.
        Args:
            grouped_segments -- list of groups of segments (= list of lists of Segment instances).
        
        Returns:
            empty string if grouped_segments is empty
            html, otherwise
        '''
        display_text_on_segment = False          #TODO should be get from somewhere
        if not grouped_segments:
            return ''
        
        # all groups should have the same width. Otherwise there would be no vertical alignment.
        group_width = self.get_width_of_group(grouped_segments[0])
        assert group_width > 0
        
        html = u'' 
        for group in grouped_segments:
            html += '<div class="group">'
            segs_total_width = 0
            for segment in group:
                seg_color_class = ['red_segment', 'green_segment'][int(segment.is_available)]       # False ~~> 0, True ~~> 1
                if isinstance(segment.end, date) and isinstance(segment.start, date):
                    seg_width = ((segment.end - segment.start).days + 1)
                else:
                    seg_width = ((segment.end - segment.start) + 1)
                segs_total_width += seg_width
                seg_width_pc = (100.0 * seg_width) / group_width                                      # pc = percentage
                seg_title = segment.get_html_str()

                html += '<div class="%s" style="width:%.3f%%"  title="%s">' % (seg_color_class, seg_width_pc, seg_title)
                if display_text_on_segment: 
                    html += seg_title
                html += '</div>  '
            html += '</div>'
#            html += '<div class="group"><br></div>'                   # spacer
        return html


    def run(self, shuffle):
        segments = [(3,4), (7,10), (5,8), (1,12), (9,11), (13,18)]
        result_segments = self.divide_colliding_segments(segments, shuffle)
        grouped_segs = self.split_segments_by_depth(result_segments)
        result_segments = []
        for group in grouped_segs:
            result_segments.append( self.add_segment_between_each_two(group) )
        pprint('segments for html:')
        pprint(result_segments)
        html = self.get_html_for_segments(result_segments)
        pprint('scale:')
        scale = self.get_html_for_scale(result_segments[0]) if result_segments else ''
        pprint(scale)
        pprint('html:')
        pprint(html)
    
    
def get_time_bar_code_for_copy(book_copy, from_date, to_date):
    '''
    Returns time bar's html for given copy and date range.
    
    Args:
        book_copy -- instance of BookCopy
        config -- instance of Config
        from_date, to_date -- instances of datetime.date . Range from which records will be displayed.
        
    Returns:
        If from_date > to_date, then empty string is returned.
    '''
    assert isinstance(book_copy, BookCopy)
    assert isinstance(from_date, date)
    assert isinstance(to_date, date)

    date_range = (from_date, to_date)
    if from_date > to_date:
        return ''
    
#    reservations = Reservation.objects.filter(book_copy=book_copy) \
#                                      .filter(Q_reservation_active) \
#                                      .filter(start_date__lte=date.today() + timedelta(config.get_int('when_reserved_period'))) \
#                                      .order_by('start_date')
    Q_start_inside_range = Q(start_date__gte=from_date) & Q(start_date__lte=to_date)  #   >   |---<--------|
    Q_end_inside_range   = Q(end_date__gte=from_date) & Q(end_date__lte=to_date)      #       |--------->--|  <
    Q_covers_whole_range = Q(start_date__lte=from_date) & Q(end_date__gte=to_date)    #   |---->----<------|
    
    reservations = Reservation.objects.filter(book_copy=book_copy) \
                                      .filter(Q_start_inside_range | Q_end_inside_range | Q_covers_whole_range) \
                                      .order_by('start_date')

    segments = [ Segment(r.start_date, r.end_date) for r in reservations ]
    # NOTE: if one would like to add some extra informations to segments, it can be done in above line 

    tb = TimeBar(one=timedelta(1))
    result_segments = tb.divide_colliding_segments(segments, shuffle=False)
    grouped_segs = tb.split_segments_by_depth(result_segments)
    
    result_segments = []
    for group in grouped_segs:
        # each of operations below may drop some segments. It may happen that all segments will be dropped.
        filled_group = tb.add_segment_between_each_two(group)
        if filled_group:
            filled_group = tb.start_with_value(filled_group, date_range[0])
        if filled_group:
            filled_group = tb.end_with_value(filled_group, date_range[1])
        if filled_group:
            result_segments.append(filled_group)
    html = tb.get_html_for_segments(result_segments)

    scale = tb.get_html_for_scale(result_segments[0]) if result_segments else ''
    if len(result_segments) > 1:
        html = scale + html + scale
    elif len(result_segments) == 1:
        html = scale + html
    return html
    
    
if __name__== '__main__': 
    t = TimeBar()
    t.run(False)

