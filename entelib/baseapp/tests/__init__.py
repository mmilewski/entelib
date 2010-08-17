# -*- coding: utf-8 -*-

PEP8_TEST_ENABLED = False

#from baseapp.tests.dbconfig import *
from baseapp.tests.page_access import *
from baseapp.tests.custom_user import *
from baseapp.tests.user_profile import *
from baseapp.tests.rental_helpers import *
from baseapp.tests.reservation_helpers import *
from baseapp.tests.views import *
from baseapp.tests.test_base import *
from baseapp.tests.reports import *
from baseapp.tests.time_bar import *
from baseapp.tests.utils import *

if PEP8_TEST_ENABLED:
    from baseapp.tests.pep8_test import *


__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}
