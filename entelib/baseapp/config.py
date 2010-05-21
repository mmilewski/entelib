from entelib.baseapp.models import Configuration


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
            assert(False and 'Config is unable to handle lists')
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

    def get_int(self, key):
        '''
        Returns integer associated with given key.
        Rises Configuration.DoesNotExist if key isn't found.
        '''
        return int(self.__getitem__(key))

    def get_bool(self, key):
        '''
        Returns True or False - legal bool value, neither 'True' nor '1'.
        Rises Configuration.DoesNotExist if key isn't found.
        '''
        value = self.__getitem__(key)
        assert(value in [Config._true_value, Config._false_value])
        return value == Config._true_value
