#-*- coding=utf-8 -*-

#
# Pass argument 'new' to create db from scratch.
#

from os import system
from sys import argv

db_file = 'database/database.db'

# if argument 'new' passed -> remove db at first
if len(argv) > 1:
    if argv[1] == 'new':
        system('rm -f %s' % db_file)

try:
    open(db_file, 'r')
except IOError:
    system('echo "no" | python manage.py syncdb')
    system('echo "import dbfiller" | python manage.py shell')
