# -*- coding: utf-8 -*-


# our base exception
class EntelibError(Exception):
    pass

class NotEnoughIDs(EntelibError):
    ''' When app runs out of new ideas how to name next copies:) '''
    pass

class EntelibWarning(EntelibError):
    ''' Used to pass warning messages, which are not errors sensu stricto '''
    pass
