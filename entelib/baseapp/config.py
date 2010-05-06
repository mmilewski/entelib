from entelib.baseapp.models import Configuration

class Config(object):
    '''
    Accesses configuration stored in database.
    '''
    def __init__(self):
        self._cached_data = {}

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
        try:
            self.__getitem__(item)
            return True
        except Configuration.DoesNotExist:
            return False

    def get_int(self, key):
        return int(self.__getitem__(key))
