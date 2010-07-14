# -*- coding: utf-8 -*-

PEP8_TEST_ENABLED = False

from baseapp.tests.dbconfig import *
from baseapp.tests.page_access import *
from baseapp.tests.custom_user import *

if PEP8_TEST_ENABLED:
    from baseapp.tests.pep8_test import *


__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}
