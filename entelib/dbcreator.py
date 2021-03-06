#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Pass argument 'new' to create db from scratch.
#

from os import system
from sys import argv, exit

db_file = 'database/database.db'

# if argument 'new' passed -> remove db at first
if len(argv) > 1:
    if argv[1] == 'new':
        system('rm -f %s' % db_file)

try:
    open(db_file, 'r')
except IOError:
    system('echo "no" | python manage.py syncdb')
    if not system('echo "import dbfiller as F \nF.main()" | python manage.py shell_plus'):
        exit(1)
