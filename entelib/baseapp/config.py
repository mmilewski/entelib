# -*- coding: utf-8 -*-

from entelib.baseapp.models import Configuration, UserConfiguration

# where is json?
try:
    from django.utils import simplejson as json
except:
    try:
        import json
    except:
        try:
            import simplejson as json
        except:
            raise


class Config(object):
    '''
    Accesses configuration stored in database.
    '''
    
    # private consts
    _true_value = u'1'           # the way that True is stored in db
    _false_value = u'0'          # the way that False is stored in db
    
    class KeyDoesNotExist(KeyError):
        pass

    class KeyCannotBeOverrided(Exception):
        pass

    def __init__(self, user=None):
        '''
        user is one for whom configuration will be customized. 
        
        NOTE:
            User can be None only if you want to register new values in Configuration (NOT 'per user configuration').
            Usages other than that can be unpredictable in effects.
        '''
        self._cached_data = {}
        self.set_user(user)
                
    def _get_all_options(self):
        ''' Returns all data from database. user must be valid. '''
        assert self.user, 'User instance is corrupted'
        config_options = Configuration.objects.all()
        overridable_options = [opt for opt in config_options if opt.can_override]
        user_options = UserConfiguration.objects.filter(user=self.user)

        result = {}
        for opt in config_options:
            result[opt.key] = opt.value
        
        for overr_option in overridable_options:
            candidate_options = [user_opt for user_opt in user_options if user_opt.option.key == overr_option.key]
            if candidate_options:
                result[overr_option.key] = candidate_options[0].value
        
        return result

    def set_user(self, user):
        ''' 
        Customizes configuration for given user.
        
        If user is None ~~> see __init__ method.
        '''
        
        self.user = user
        if user:
            self._cached_data = self._get_all_options()
        else:
            self._cached_data = {}
    
    def clear(self, truncate_model=False):
        ''' Clears cache. If truncate_model is set, removes all data from Configuration model. '''
        self._cached_data = {}
        if truncate_model:
            Configuration.objects.all().delete()

    def __getitem__(self, key):
        ''' 
        Gets key from config & returns it's value.
        If value is not found, then Configuration.DoesNotExist is raised.
        '''
        if key in self._cached_data:
            return self._cached_data[key]
        else:
            try:
                option = Configuration.objects.get(key=key)
                self._cached_data[key] = option.value
                return option.value
            except Configuration.DoesNotExist, e:
                # print Configuration.objects.all()
                raise Configuration.DoesNotExist(e.args + (key,))

    def __setitem__(self, key, value):
        '''
        Sets value of key.
        
        It properly reveals types of value given if it (value's type) is one of following:
        boolean, int, string, list.
        
        May raise Config.KeyCannotBeOverrided if one tries to violate this. Can be checked with
        config.can_override method - check it's description for more details.
        
        Note: It is recommended to set values' via setters like set_int, set_list, ...
        '''
        
        # check if overriding is possible. This function allows to create
        # options and then overriding shouldn't be checked
        if (key in self) and (not self.can_override(key)):
            raise Config.KeyCannotBeOverrided
        
        # reveal how value should be stored in model
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
            
        # insert new key, value pair
        if key not in self:
            record = Configuration(key=key, value=value, description='')
            record.save()
        # update value
        else:
            can_override = self.can_override(key, silent=False)
            if self.user and can_override:
                config_option = Configuration.objects.get(key=key)
                result, created = UserConfiguration.objects.get_or_create(option=config_option, 
                                                                          defaults={'user': self.user, 'value': value})
                result.save()
        
        # update cache
        self._cached_data[key] = value
        
    def __contains__(self, key):
        ''' Checks if item is in configuration. Returns True or False. '''
        try:
            self.__getitem__(key)
            return True
        except Configuration.DoesNotExist:
            return False

    def has_key(self, key):
        ''' Checks if key is in configuration. '''
        return self.__contains__(key)
    
    def can_override(self, key, silent=True):
        ''' 
        Checks if value of given key can be overriden.
        If returning False, then see note below
        
        May raise Configuration.KeyDoesNotExist.
        If silent is True, then Configuration.KeyDoesNotExist will never be raised. If so, then
        returning False may also mean that key wasn't found.
        '''
        option = None
        try:
            option = Configuration.objects.only('can_override').get(key=key)
        except Configuration.DoesNotExist:
            if not silent:
                raise Config.KeyDoesNotExist
        return option.can_override if option else False
    
    # set description
    def set_description(self, key, desc):
        '''
        Sets description of given key.
        Description is set in Configuration, so this option is not for normal users. Also no permissions are checked.
        '''
        try:
            result = Configuration.objects.get(key=key)
        except Configuration.DoesNotExist, e:
            raise Configuration.DoesNotExist(e.args + (key,))
        result.description = desc
        result.save()

    # get description
    def get_description(self, key):
        '''
        Gets description of given key.
        '''
        try:
            result = Configuration.objects.get(key=key)
        except Configuration.DoesNotExist, e:
            raise Configuration.DoesNotExist(e.args + (key,))
        return result.description

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
