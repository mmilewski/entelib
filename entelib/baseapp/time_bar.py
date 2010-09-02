# -*- coding: utf-8 -*-
import random
from copy import copy
from datetime import date, timedelta
from fractions import gcd
from baseapp.utils import pprint, str_to_date, create_days_between, week_for_day,\
    month_for_day
import views_aux as aux
from baseapp.models import Reservation, BookCopy
from django.db.models.query_utils import Q
from django.core.handlers.wsgi import WSGIRequest
from itertools import groupby
from baseapp.config import Config
import datetime


def timedelta_as_int(delta):
    """ Converts timedelta to integer (days). If delta is int, does nothing."""
    if isinstance(delta, timedelta):
        return delta.days
    assert isinstance(delta, int)
    return delta


class Segment(object):
    
    def __init__(self, start, end, z=0, is_available=False):
        self.start = start
        self.end = end
        self.z = z                         # z-plane
        self.is_available = is_available   # as default Segment instance is unavailable (not rentable or sth)
    
    @classmethod
    def from_tuple(cls, tuple):
        """ Creates instance from tuple. It may be done to work with iterable, but is not needed now."""
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
        """ 
        Returns string for displaying in html. __unicode__ is not used, because 
        it returns the simplest representation of Segment -- very useful in test.
        """
        rentable_caption = 'rentable' if self.is_available else 'not rentable'
        if hasattr(self, 'who_reserved'):
            who = aux.user_full_name(self.who_reserved, True)
            return u'(%s, %s) %s. Who: %s' % (self.start, self.end, rentable_caption, who)
        else:
            return u'(%s, %s) %s' % (self.start, self.end, rentable_caption)
    
    def increment_z(self, by_value=1):
        """ Increases self.z by given value."""
        self.z += by_value
    
    def check_invariant(self):
        """ This should always be True. """
        if self.start > self.end:
            return False
        if self.z < 0:
            return False
        return True
    
    def collides_with(self, other):
        """ 
        Returns True iff self collides with other.
        
        Args:
            other -- Segment instance
            
        Note: (_,5,_) collides with (5,_,_)
        """
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
        """ 
        Checks if self collides with at least one of segments in haystack.
        
        Args:
            haystack -- list of Segment objects
        
        Returns:
            True or False respectively.
        """
        assert self.check_invariant()
        
        for needle in haystack:
            if self.collides_with(needle):
                return True
        return False



class TimeBar(object):
    
    def __init__(self, config, one=1):
        """
        Args:
            config -- instance of Config.
            one -- smallest portion of data. Like 'one day' or '1'. This may be useful when 
                   you want to test using ints and later use dates instead.
        """
        self.config = config
        self.one = one

    def get_segments_depth(self, segments):
        """ 
        Returns number of unique z-planes for given segments. 
    
        Args:
            segments -- list of Segment objects
        """
        return len(set( [s.z for s in segments] ))

    def _assure_segment(self, segment):
        """ 
        Returns new instance of Segment.
        Args:
            segment -- tuple or Segment instance.
        """
        if isinstance(segment, Segment):
            return copy(segment)
        if isinstance(segment, tuple):
            return Segment.from_tuple(segment)
        assert False, 'unknown type'

        
        
    def divide_colliding_segments(self, segments, shuffle=False):
        """ 
        Divides segments into multiple planes. So this function returns the same segments 
        but with additional coordinate - like z-plane.
        
        Args:
            segments -- list Segmant objects or 2-tuples. About each 2-tuple you can think as (start, end).
            shuffle -- if True then segments will be shuffled before use, so algorithm will be randomized.
            
        Returns:
            list of Segment objects. Result is not sorted.
        """
        segments_left = [self._assure_segment(s) for s in segments]
        if len(segments_left) < 2:
            return segments_left
        
        max_iterations = 10                     # more then this number of iteration means an error probably
        if shuffle:
            random.shuffle(segments_left)
        result = []
        iterations = 0
        while segments_left:
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
        assert len(result) == len(segments) or len(result) == max_iterations
        for seg in result:
            tmp_result = list(result)
            tmp_result.remove(seg)         # seg collides with seg, so it should be removed before assert
            assert not seg.collides_with_list(tmp_result)
        
        return result
        
        
    def add_segment_between_each_two(self, segments):
        """
        Between each two segments adds additional segment. But only if there is
        free space for that. Between (1,4,0) and (5,10,0) there is no such space.
        
        Args:
            segments -- list of Segment objects. All must have the same z-value.
                        Should be sorted by start field.
        """
        if len(segments) < 2:
            return segments
        
        modified_segs = []
        segs_count = len(segments)
        
        for i in range(segs_count-1):
            assert segments[i].z == segments[i+1].z
            old_seg = segments[i]
            modified_segs.append(old_seg)
            should_add = timedelta_as_int(segments[i+1].start - segments[i].end) > 1
            if should_add:
                new_seg = Segment(old_seg.end + self.one, segments[i+1].start - self.one , old_seg.z)
                new_seg.is_available = True
                modified_segs.append(new_seg)
        modified_segs.append(segments[-1])
        return modified_segs
        
        
    def split_segments_by_depth(self, segments, sort=False):
        """
        Splits segments by z coord.
        
        Args:
            segments -- list of Segment instances. z values must not cantain any gap,
                        and must start with 0. So if there are 3 distinct depths, then
                        z-value of highest is 2.
            sort -- if True then each group will be sorted.
        
        Returns:
             List of lists, one for each group. Groups' z values are sorted ascending.
             Groups are sorted by start value, if sort is True.
        """
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
        """ 
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
        """
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
        """
        Works similar to start_with_value.
        """
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
                seg = result[-1]                   #                    ^     <--- this says where end_value is
                new_seg = Segment(start=seg.end + self.one, end=end_value, z=seg.z, is_available=True)
                result.append(new_seg)
            elif result[-1].end > end_value:    #  |------|-------|
                result[-1].end = end_value      #             ^
        return result
    
    
    def get_width_of_group(self, group):
        """
        Returns width of group, which means total number of units.
        i.e. width of date range 2010-07-01, 2010-07-10 is 10 (ten days).
        
        Args:
            group -- list of Segment instances.
            
        Returns:
            If group is empty, then returns -1
        """
        if not len(group):
            return -1
        group_width = timedelta_as_int(group[-1].end - group[0].start) + 1
        return group_width
    
    
    def get_html_of_scale(self, groups):
        """
        Returns html for scale (podziałka).
        
        Args:
            groups -- groups of segments (list of list of Segment instances).
            
        Raises:
            If group is empty, then raises ValueError
        """
        if not groups:
            raise ValueError('Given groups is empty: %s' % (repr(groups)))
        
        max_days_to_display_days = self.config.get_int('tb_max_days_to_display_days')
        max_days_to_display_weeks = self.config.get_int('tb_max_days_to_display_weeks')
        max_days_to_display_days  = max(1, max_days_to_display_days)    # at least one day
        max_days_to_display_weeks = max(1, max_days_to_display_weeks)   # at least one day 
        if max_days_to_display_days >= max_days_to_display_weeks:        # _days should be < _weeks
            max_days_to_display_days = max_days_to_display_weeks - 1
        
        width = self.get_width_of_group(groups[0])
        display_days = width <= max_days_to_display_days
        display_weeks = (not display_days) and width <= max_days_to_display_weeks
        display_months = (not display_days) and (not display_weeks)
        
        first_day, last_day = groups[0][0].start, groups[0][-1].end
        days_in_range = create_days_between(first_day, last_day, include_start=True, include_end=True)
        html = ''
        if display_days:
            html = u'<div class="scaleWrapper">'
            for day in days_in_range:
                title = unicode(day)
                html += u'<div class="scale_part" style="width: %.3f%%" title="%s">' % (100.0 / width, title)
                html += title
                html += u'</div>'
            html += u'</div>'            
        elif display_weeks:
            week_to_first_day_map = {}
            for day in days_in_range:
                wfd = week_for_day(day) 
                if wfd not in week_to_first_day_map:
                    week_to_first_day_map[wfd] = day
            
            weeks_in_range = [week_for_day(day) for day in days_in_range]
            grouped_weeks = [(key[0],key[1],len(list(group))) for key,group in groupby(weeks_in_range)]  # [year, week_nr, len]
            display_year = len(set([y for y,n,c in grouped_weeks])) > 1
            html = u'<div class="scaleWrapper">'
            for year,week_nr,week_len in grouped_weeks:
                first_day = week_to_first_day_map[(year,week_nr)]
                period_name = u'%s, %d (%dw)' % (first_day.strftime('%B'), first_day.day, week_nr)
                hover_title = period_name
                if display_year:
                    title = u'%d week of %d' % (week_nr, year)
                else:
                    title = u'%d week' % (week_nr,)
                html += u'<div class="scale_part" style="width: %.3f%%" title="%s">' % (100.0 * week_len / width, hover_title)
                html += title
                html += u'</div>'
            html += u'</div>'
        elif display_months:
            months_in_range = [month_for_day(day) for day in days_in_range]
            grouped_months = [(key[0],key[1],len(list(group))) for key,group in groupby(months_in_range)]  # [year, month_nr, len]
            display_year = len(set([y for y,m,c in grouped_months])) > 1
            html = u'<div class="scaleWrapper">'
            for year,month_nr,week_len in grouped_months:
                title = u'%d-%d' % (year, month_nr)
                html += u'<div class="scale_part" style="width: %.3f%%" title="%s">' % (100.0 * week_len / width, title)
                html += title
                html += u'</div>'
            html += u'</div>'
        else:
            assert False, 'Unknown type of scale. Are values in configuration correct?'

#        # count gcd
#        the_gcd = self.gcd_for_group(groups[0])
#        for group in groups:
#            the_gcd = gcd(the_gcd, self.gcd_for_group(group))
        
        return html
        
        
    def gcd_for_group(self, group):
        """
        Return greates common divisor for lengths of segments in group.
        
        If group is empty, raises ValueError.
        """
        if not group:
            raise ValueError('Cannot get gcd for empty group')

        cur_gcd = timedelta_as_int(group[0].end - group[0].start) + 1
        for seg in group:
            cur_gcd = gcd(cur_gcd, timedelta_as_int(seg.end - seg.start) + 1)
            if cur_gcd < 2:
                return cur_gcd
        return cur_gcd
        
        
    def get_html_for_segments(self, grouped_segments):
        """
        Returns html for given groups of segments.
        Args:
            grouped_segments -- list of groups of segments (= list of lists of Segment instances).
        
        Returns:
            empty string if grouped_segments is empty
            html, otherwise
        """
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
                seg_width = timedelta_as_int(segment.end - segment.start) + 1
                segs_total_width += seg_width
                seg_width_pc = (100.0 * seg_width) / group_width                                    # pc = percentage
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
        scale = self.get_html_of_scale(result_segments) if result_segments else ''
        pprint(scale)
        pprint('html:')
        pprint(html)
    
    
def get_time_bar_code_for_copy(config, book_copy, from_date, to_date):
    """
    Returns time bar's html for given copy and date range.
    
    Args:
        book_copy -- instance of BookCopy
        config -- instance of Config
        from_date, to_date -- instances of datetime.date . Range from which records will be displayed.
        
    Returns:
        If from_date > to_date, then empty string is returned.
    """
    assert isinstance(book_copy, BookCopy)
    assert isinstance(from_date, date)
    assert isinstance(to_date, date)

    date_range = (from_date, to_date)
    if from_date > to_date:
        return ''
    
    Q_start_inside_range = Q(start_date__gte=from_date) & Q(start_date__lte=to_date)  #   >   |---<--------|
    Q_end_inside_range   = Q(end_date__gte=from_date) & Q(end_date__lte=to_date)      #       |--------->--|  <
    Q_covers_whole_range = Q(start_date__lte=from_date) & Q(end_date__gte=to_date)    #   |---->----<------|
    
    reservations = Reservation.objects.filter(book_copy=book_copy) \
                                      .filter(when_cancelled=None) \
                                      .filter(Q(rental=None)|Q(rental__end_date=None)) \
                                      .filter(Q_start_inside_range | Q_end_inside_range | Q_covers_whole_range) \
                                      .order_by('start_date')

    segments = []
    for r in reservations:
        seg = Segment(r.start_date, r.end_date)
        seg.who_reserved = r.for_whom
        segments.append(seg)
    # NOTE: if one would like to add some extra informations to segments, it can be done above.
    #       This is why segment is an object and not a tuple.

    # ok, we gathered segments, now let's create time bar on top of them
    tb = TimeBar(config, one=timedelta(1))
    result_segments = tb.divide_colliding_segments(segments, shuffle=False)   # detect collisions
    grouped_segs = tb.split_segments_by_depth(result_segments)                # and collect them in groups
    
    # set number of colliding groups. Cut surplus. 
    max_colliding_groups = 5 
    grouped_segs = grouped_segs[:max_colliding_groups]
    
    # "correct" each group, which means add "green segments" in between, cut/enlarge start and end dates properly
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
    
    # if there is no reservations, then add available one-Segment group
    if not result_segments:
        group = [Segment(from_date, to_date, is_available=True)]
        result_segments.append(group)
    
    # generate html
    html = tb.get_html_for_segments(result_segments)

    # add scale (or two scales if there is a lot of colliding segments)
    scale = tb.get_html_of_scale(result_segments) if result_segments else ''
    if len(result_segments) > 100000:
        html = scale + html + scale
    elif len(result_segments) > 0:
        html = scale + html
    return html
    
    
class TimeBarRequestProcessor(object):
    
    def __init__(self, request_data, default_date_range, config):
        """
        Args:
            request_data -- dict-like object, from which one can retrieve info about time bar form.
                            Usually request.post is a good choice. If None, then default values will be used.
                            If request_data is request from django's view (WSGIRequest, 
                            then it will be handled properly (i.e. will look for request.POST).
            default_date_range -- 2-tuple or 2-list, default from_, and to_date.
            config -- instance of Config
        """
        self.config = config
        
        # request_date
        self.request = request_data
        if isinstance(self.request, WSGIRequest):
            if self.request.method == 'POST':
                self.request = self.request.POST     
            else:
                self.request = None
        
        # default_date_range
        if default_date_range:
            self.default_date_range = list(default_date_range)
        else:
            self.default_date_offset = timedelta(config.get_int('when_reserved_period'))
            default_from_date = date.today() - timedelta(3)
            default_to_date = default_from_date + self.default_date_offset
            self.default_date_range = [default_from_date, default_to_date]
            
        assert len(self.default_date_range) == 2, 'invalid default date range'
        assert isinstance(self.default_date_range[0], date)
        assert isinstance(self.default_date_range[1], date)
        
    def _cut_date_range_if_too_wide(self, date_range):
        """
        Checks if date range is longer then value in config (tb_max_days_in_date_range).
        If so it would be cut. 
        Length of range between (2010,1,25) and (2010,1,30) equals 5 days.
        
        Args:
            date_range -- 2-tuple or 2-list of date instances - start and end, where start <= end
        
        Returns:
            "Correct" date range as 2-tuple.
        """
        assert len(date_range) == 2
        assert isinstance(date_range[0], date)
        assert isinstance(date_range[1], date)
        start, end = date_range
        max_days_in_range = self.config.get_int('tb_max_days_in_date_range')
        if (end - start).days > max_days_in_range:
            end = start + timedelta(max_days_in_range)
        return (start, end)

        
    def handle_request(self):
        """
        Reads data from self.request and return dict with data useful for response context.

        If self.request is None, then default values are used (access via GET probably).
        If self.request is set, then checks what button was pressed (access via POST probably).
        If start_date or end_date value is incorrect (not valid date), then defaults
        are used respectively.  
        """ 
        post = self.request
        result = {}
        date_range = self.default_date_range
        if post:
            btn_custom_hit        = 'tb_btn_custom_date' in post
            btn_default_range_hit = 'tb_btn_default_range' in post
            btn_next_30_days_hit  = 'tb_btn_next_30_days' in post
            btn_next_60_days_hit  = 'tb_btn_next_60_days' in post
            btn_next_90_days_hit  = 'tb_btn_next_90_days' in post
            
            # which button was pressed? What action should be triggered?
            if btn_custom_hit:
                date_range = [str_to_date(post['tb_from_date']), str_to_date(post['tb_to_date'])]
            elif btn_default_range_hit:
                date_range = self.default_date_range
            elif btn_next_30_days_hit:
                date_range = [date.today(), date.today() + timedelta(30)]
            elif btn_next_60_days_hit:
                date_range = [date.today(), date.today() + timedelta(60)]
            elif btn_next_90_days_hit:
                date_range = [date.today(), date.today() + timedelta(90)]

        # if posted date is incorrect, then set default values
        date_range[0] = date_range[0] or self.default_date_range[0]    # override if None
        date_range[1] = date_range[1] or date_range[0] + self.default_date_offset

        # create result dict
        cut_date_range = self._cut_date_range_if_too_wide(date_range)
        result['date_range'] = cut_date_range
        return result


    def get_context(self, copy=None):
        """
        Returns request context.
        
        Args:
            copy -- instance of BookCopy. You can use it instead of calling get_code_for_copies([copy])

        Returns:
            dict -- intended to be used like context.update(time_bar_context)
                    { display_time_bar, tb_from_date, tb_to_date, tb_code }, tb_code is present if copy is not None.
        """ 
        request_values = self.handle_request()
        from_date, to_date = request_values['date_range']
        display_time_bar = self.config.get_bool('enable_time_bar')
        context = {
            'display_time_bar': display_time_bar,
            'tb_from_date': from_date,
            'tb_to_date': to_date,
        }

        if copy:
            assert isinstance(copy, BookCopy)
            code = get_time_bar_code_for_copy(self.config, copy, from_date=from_date, to_date=to_date)
            context['tb_code'] = code
        return context
    
    def get_codes_for_copies(self, copies):
        """
        Return html for given copy.
        
        Args:  
            copies -- list of copies (BookCopy objects), for which time bar will be generated.
            
        Returns:
            dict { copy.id : time-bar-html-code }
        """
        request_values = self.handle_request()
        from_date, to_date = request_values['date_range']
        
        codes = {}
        for copy in copies:
            codes[copy.id] = get_time_bar_code_for_copy(self.config, copy, from_date=from_date, to_date=to_date)
        return codes


if __name__== '__main__':
    config = Config() 
    t = TimeBar(config)
    t.run(False)

