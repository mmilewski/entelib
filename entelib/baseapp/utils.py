# -*- coding: utf-8 -*-

from pprint import pprint   # pretty printer
import datetime

def str_to_date(str):
    ''' 
    Converts given string into datetime.date object. String should be like '2010-07-25'.
    If conversion fails - returns None.
    '''    
    try:
        parsed_date = datetime.datetime.strptime(str, "%Y-%m-%d")
    except ValueError:
        return None
    else:
        return parsed_date.date()
    return None


def today():
    return datetime.date.today()
    
def tomorrow():
    return today() + datetime.timedelta(1)
    
def after_days(n, since=None):
    ''' Returns date n days after since. If since is not given, today is used.'''
    since = since or today()
    return since + datetime.timedelta(n)


def remove_non_ints(items):
    '''
    Filters items selecting those, which can be converted to int. 
    Returns list of items converted to int.

    Args:
        items -- iterable. List of any kind of objects.

    Returns:
        List of ints.
    '''
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
    ''' 
    Returns list of days between start and end. Ends are included respectively to include_start and include_end.
    If start==end, then start will be included iff at least one of include_* is True.
    
    Args:
        start -- date object.
        end -- date object.
    '''
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
    ''' Returns year and number of week for given day.'''
    year, week_nr, weekday = day.isocalendar()  #@UnusedVariable
    return (year, week_nr)


def month_for_day(day):
    ''' Returns year and month for given day. Month number contains in [1..12].'''
    return (day.year, day.month)

