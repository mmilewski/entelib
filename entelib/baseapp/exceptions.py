# -*- coding: utf-8 -*-


# our base exception
class EntelibError(Exception):
    pass

class EntelibWarning(EntelibError):
    ''' Used to pass warning messages, which are not errors sensu stricto '''
    pass
