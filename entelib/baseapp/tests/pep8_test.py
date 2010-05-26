from django.test import TestCase
import sys
from StringIO import StringIO
import pep8

# see: http://www.dominno.pl/2010/02/15/automatyczne-sprawdzanie-zgodnosci-kodu-pythona/
#      http://www.python.org/dev/peps/pep-0008/


class PEP8TestCase(TestCase):
    def test_pep8_rules(self):
        sys.argv[1:] = ['--filename=*.py',
                        '--show-source',
                        '--show-pep8',
                        '--ignore=E201,E202,E203,E221,E222,E231,E241,E251,E303,E501',
                        '--repeat',
                        '--exclude=tagging',
                        './']
        buf = StringIO()
        sys.stdout = buf
        pep8._main()
        sys.stdout = sys.__stdout__
        result = buf.getvalue()

        self.assertEqual("", result, "Code messages should be empty but was:\n" + result)
