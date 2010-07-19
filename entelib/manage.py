#!/usr/bin/python

# inject specific version of Django and Imaging (PIL)
# Where should be Django-1.2.1? Here is dump of  tree -L 2
# .
# |-- entelib
# |   |-- __init__.py
# |   |-- auth_backends.py
# |   |-- baseapp
# |   |-- database
# |   |-- dbconfigfiller.py
# |   |-- dbcreator.py
# |   |-- dbfiller.py
# |   |-- email
# |   |-- manage.py
# |   |-- media
# |   |-- run.sh
# |   |-- settings.py
# |   |-- shell.sh
# |   |-- templates
# |   `-- urls.py
# `-- libs
#     |-- Django-1.2.1
#     |   |-- (...)
#     |   `-- django
#     `-- Imaging-1.1.7
#     |   |-- (...)
#     |   `-- PIL

PRINT = lambda x: x

from os.path import abspath, dirname, join, exists
import sys
libs_path = join(dirname(abspath(__file__)),'..','libs')
django_path = join(libs_path,'Django-1.2.1')
imaging_path = join(libs_path,'Imaging-1.1.7')
PRINT('Special Django path %s' % ('was found' if exists(django_path) else "wasn't found at " + django_path))
PRINT('Special Imaging path %s' % ('was found' if exists(imaging_path) else "wasn't found at " + imaging_path))
sys.path.insert(0, imaging_path)
sys.path.insert(0, django_path)


# original content
from django.core.management import execute_manager
try:
    import settings  # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)
