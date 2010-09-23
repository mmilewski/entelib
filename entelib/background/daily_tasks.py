import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../..')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


from os.path import abspath, dirname, join, exists
project_path = join(dirname(abspath(__file__)), '..')
app_path = join(project_path, '..', 'baseapp')
libs_path = join(dirname(abspath(__file__)),'../..','libs')
django_path = join(libs_path,'Django-1.2.1')
imaging_path = join(libs_path,'Imaging-1.1.7')
sys.path.insert(0, imaging_path)
sys.path.insert(0, django_path)
sys.path.insert(0, project_path)
sys.path.insert(0, app_path)


from baseapp.models import *
from django.contrib.auth.models import User
from baseapp.utils import today

for r in Rental.objects.all():
    if not r.end_date :
        if r.reservation.end_date < today():
            print r
    
