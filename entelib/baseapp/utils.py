# -*- coding: utf-8 -*-

from pprint import pprint   # pretty printer
import datetime

def str_to_date(str):
    ''' 
    Converts given string into datetime.date object. String should be like '2010-07-25'.
    If convertion fails - returns None.
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
    
def after_days(n):
    today() + datetime.timedelta(n)
