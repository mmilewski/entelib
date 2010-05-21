from entelib.baseapp.models import Configuration
import json


class Config(object):
    '''
    Accesses configuration stored in database.
    '''

    # private consts
    _true_value = u'1'           # the way that True is stored in db
    _false_value = u'0'          # the way that False is stored in db


    def __init__(self):
        self._cached_data = {}

    def clear(self, truncate_model=False):
        ''' Clears cache. If truncate_model is set, removes all data from Configuration model. '''
        self._cached_data = {}
        if truncate_model:
            Configuration.object.all().delete()

    def __getitem__(self, key):
        if key in self._cached_data:
            return self._cached_data[key]
        else:
            try:
                result = Configuration.objects.get(key=key)
                self._cached_data[key] = result.value
                return result.value
            except Configuration.DoesNotExist, e:
                raise e

    def __setitem__(self, key, value):
        if value == True:
            value = Config._true_value
        elif value == False:
            value = Config._false_value
        elif isinstance(value, list):
            value = json.dumps(value)
        elif isinstance(value, dict):
            assert(False and 'Config is unable to handle dicts')
        else:
            value = unicode(value)
        self._cached_data[key] = value

        # update
        try:
            result = Configuration.objects.get(key=key)
            result.value = value
            result.save()
            return
        except Configuration.DoesNotExist, e:
            # insert
            record = Configuration(key=key, value=value)
            record.save()

    def __contains__(self, item):
        ''' Checks if item is in configuration. Returns True or False. '''
        try:
            self.__getitem__(item)
            return True
        except Configuration.DoesNotExist:
            return False

    # str
    def get_str(self, key):
        '''
        Returns unicode string associated with given key.
        Raises Configuration.DoesNotExist if key isn't found.
        '''
        return unicode(self.__getitem__(key))

    def set_str(self, key, value):
        value = unicode(value)
        self.__setitem__(key, value)

    # int
    def get_int(self, key):
        '''
        Returns integer associated with given key.
        Raises Configuration.DoesNotExist if key isn't found.
        Raises ValueError iff int(key) does.
        '''
        return int(self.__getitem__(key))

    def set_int(self, key, value):
        '''
        Associates integer value with key.
        Raises ValueError iff int(key) does.
        '''
        value = int(value)
        self.__setitem__(key, value)

    # bool
    def get_bool(self, key):
        '''
        Returns True or False - legal bool value, neither 'True' nor '1'.
        Raises Configuration.DoesNotExist if key isn't found.
        '''
        value = self.__getitem__(key)
        assert(value in [Config._true_value, Config._false_value])
        return value == Config._true_value

    def set_bool(self, key, value):
        value = bool(value)
        self.__setitem__(key, value)

    # list
    def get_list(self, key):
        '''
        Returns list.
        Raises Configuration.DoesNotExist if key isn't found.
        Raises ValueError if value associated with key is not a list.
        '''
        value = self.__getitem__(key)
        value = json.loads(value)
        return value

    def set_list(self, key, value):
        '''
        Associates list with given key.
        Raises ValueError if value associated with key is not a list.
        '''
        value = list(value)
        self.__setitem__(key, value)   # json.dumps is done in __setitem__
