from os.path import abspath, dirname, join, exists
import sys
libs_path = join(dirname(abspath(__file__)),'../..','libs')
django_path = join(libs_path,'Django-1.2.1')
imaging_path = join(libs_path,'Imaging-1.1.7')
sys.path.insert(0, imaging_path)
sys.path.insert(0, django_path)
from django.contrib.auth.models import *
from baseapp.models import *

import pickle
filename = raw_input(['In what file store passwords? [Enter] for "passwords.back"'])
if not filename:
    filename = 'passwords'
filename = 'migration/' + filename

file = open(filename, 'w')
email_hash_list = User.objects.values_list('email', 'password')
pickle.dump(email_hash_list, file)
file.close()
