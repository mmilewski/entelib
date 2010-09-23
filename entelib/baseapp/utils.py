# -*- coding: utf-8 -*-

from pprint import pprint   # pretty printer
import logging
import datetime
from django.contrib.auth.models import User


def str_to_date(str, default=None):
    """ 
    Converts given string into datetime.date object. String should be like '2010-07-25'.
    If conversion fails - returns default.
    """    
    try:
        parsed_date = datetime.datetime.strptime(str, "%Y-%m-%d")
    except ValueError:
        return default
    else:
        return parsed_date.date()
    return default


def today():
    return datetime.date.today()
    
def tomorrow():
    return today() + datetime.timedelta(1)
    
def after_days(n, since=None):
    """ Returns date n days after since. If since is not given, today is used."""
    since = since or today()
    return since + datetime.timedelta(n)


def remove_non_ints(items):
    """
    Filters items selecting those, which can be converted to int. 
    Returns list of items converted to int.

    Args:
        items -- iterable. List of any kind of objects.

    Returns:
        List of ints.
    """
    filtered_items = []
    for item in items:
        try:
            if isinstance(item, basestring):
                item = item.strip()
            item = int(item)
        except (ValueError, TypeError):
            pass
        else:
            filtered_items.append(item)
    return filtered_items


def create_days_between(start, end, include_start=True, include_end=True):
    """ 
    Returns list of days between start and end. Ends are included respectively to include_start and include_end.
    If start==end, then start will be included iff at least one of include_* is True.
    
    Args:
        start -- date object.
        end -- date object.
    
    Returns:
        list of Date (or DateTime if start is DateTime) instances.
    """
    if start > end:
        return []
    
    one_day = datetime.timedelta(1)
    result = []
    curr_date = start
    while curr_date <= end:
        if curr_date == start and include_start:
            result.append(curr_date)
        elif curr_date == end and include_end:
            result.append(curr_date)
        elif start < curr_date < end:
            result.append(curr_date)
        else:
            pass # start or end but corresponding include is False
        curr_date += one_day
    return result
    
    
def week_for_day(day):
    """ Returns year and number of week for given day."""
    year, week_nr, weekday = day.isocalendar()  #@UnusedVariable
    return (year, week_nr)


def month_for_day(day):
    """ Returns year and month for given day. Month number contains in [1..12]."""
    return (day.year, day.month)


def order_asc_by_key(key):
    return lambda a,b: -1 if a[key] < b[key] else ( 1 if a[key] > b[key] else 0)
    
def order_desc_by_key(key):
    return lambda a,b:  1 if a[key] < b[key] else (-1 if a[key] > b[key] else 0)


def get_admins():
    users = User.objects.all()
    admins = [u for u in users if u.userprofile.is_admin()]
    return admins


logger_names = ['view.forgot_password', 'config', 'config.option', 'view.show_book_copy', ]

def get_logger(name):
    if name not in logger_names:
        propositions = LevenshteinDistance( name, logger_names).most_accurate(2)
        raise ValueError("Logger name wasn't found. Did you mean %s" % ' or '.join(propositions))
    logger = logging.getLogger(name)
    # logger.addHandler(logging.StreamHandler())
    return logger


class LevenshteinDistance(object):
    def __init__(self, s, t, mode='lowersort'):
        """
        Args:
            s - always a string
            t - string or a list of strings. Depends on function you will use later.
            sort - 'lowersort'  - characters of s and t will be lowercased, then sorted before comparison.
                   'sort'       - characters of s and t sorted before comparison.
                   'lower'      - strings will be lowercased befor comparison.
                   'mixed'      - uses few methods, and selects most accurate results. May be slow.
                   'id'         - identity
                   Otherwise 'id' will be used
        """
        self.s = s
        self.t = t
        self.mode = mode

        if self.mode == 'mixed':
            self.mode = 'lowersort'
        transform = lambda x: x
        if self.mode == 'lowersort':  transform = lambda x: ''.join(sorted(x.lower()))
        elif self.mode == 'sort':     transform = lambda x: ''.join(sorted(x))
        elif self.mode == 'lower':    transform = lambda x: x.lower()
        elif self.mode == 'id':       transform = lambda x: x
        self.transform = transform

    def distance(self):
        """
        Requires self.t to be string.
        Returns distance of s and t.
        """
        assert isinstance(self.t, basestring)
        s, t = ' ' + self.transform(self.s), ' ' + self.transform(self.t)
        S, T = len(s), len(t)
        d = {}
        for i in range(S):
            d[i, 0] = i
        for j in range (T):
            d[0, j] = j
        for j in range(1,T):
            for i in range(1,S):
                if s[i] == t[j]:
                    d[i, j] = d[i-1, j-1]
                else:
                    d[i, j] = min(d[i-1, j] + 1, d[i, j-1] + 1, d[i-1, j-1] + 1)
        return d[S-1, T-1]

    def distance_tuple(self):
        """
        Returns pair: (distance, t_string)
        """
        return (self.distance(), self.t)

    def most_accurate_tuples(self, n=1):
        """
        Requires self.t to be a list of strings.
        """
        assert isinstance(self.t, list)
        if not self.t:
            raise ValueError('Empty list')
        f = lambda x: LevenshteinDistance(self.s, x, mode=self.mode).distance_tuple()
        return list(sorted(map(f, self.t)))[:n]

    def most_accurate(self, n=1):
        return zip(*self.most_accurate_tuples(n))[1]



class AutocompleteHelper(object):
    def __init__(self, items=[], string=''):
        """
        Args:
            items -- iterable. List of items that will be converted to string.
            str -- basestring. String describing list which will be parsed.
        """
        self.items = list(items)
        self.string = string

    def as_str(self, sep=', ', delim='"'):
        """
        In constructor 'items' should be given.
        """
        items = [ unicode(x).replace('"','') for x in self.items ]
        items = [ ('%s%s%s' % (delim,i,delim)) for i in items ]
        result = sep.join(items)
        return result

    def from_str(self, sep=","):
        """
        In constructor 'str' should be given.
        """
        names = self.string
        names = names.replace("u'", '').replace('u"', '')    # naive method of parsing. How to do it better?
        names = names.replace('"', '')
#         names = names..replace("'", '')                    # single quote may be usefull in names
        names = names.replace('[', '').replace("]", '')
        list_of_names = names.split(sep)
        list_of_names = [name.strip() for name in list_of_names if len(name.strip())]
        return list_of_names
