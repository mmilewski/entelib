# -*- coding: utf-8 -*-

from pprint import pprint   # pretty printer
import datetime

def str_to_date(str):
    ''' 
    Converts given string into datetime.date object. String should be like '2010-07-25'.
    If convertion fails - returns None.
    '''
    parts = str.split('-')
    if len(parts) != 3:
        return None
    try:
        values = map(int, parts)
    except ValueError:
        return None
    else:
        return datetime.date(*values)
    return None
