#-*- coding=utf-8 -*-  
try:
    open('database/database.db','r')
except:
    from os import system
    system('echo "no" | python manage.py syncdb')
    system('echo "import dbfiller" | python manage.py shell')

