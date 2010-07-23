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
    
    class Option(object):
        def __init__(self, key, value, description, can_override):
            self.key = key
            self.value = value
            self.can_override = can_override
            self.description = description
        
        def __unicode__(self):
            return u'%s %s %s' % (self.can_override, self.key, self.value)


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
                
    def get_all_key_value_options(self):
        ''' 
        Returns configuration options as dict[key]=value. 
        If you need more details (like can_override) check out get_all_options method.
        
        self.user must be valid when running this method.
        '''
        
        result = self.get_all_options()
        for key, opt in result.items():
            result[key] = opt.value

        return result
    
    def get_all_options(self):
        '''
        Gets all config options and returns it as a dict of Config.Option records -- { key: option }
        
        self.user must be valid.
        '''
        assert self.user, 'User instance is corrupted'
        
        
        config_options = Configuration.objects.all()
        overridable_options = [opt for opt in config_options if opt.can_override]
        user_options = UserConfiguration.objects.filter(user=self.user)

        result = {}
        for opt in config_options:
            option = Config.Option(key=opt.key, value=opt.value, can_override=opt.can_override, description=opt.description)
            result[opt.key] = option
        
        # override some options
        for overr_option in overridable_options:
            candidate_options = [user_opt for user_opt in user_options if user_opt.option.key == overr_option.key]
            if candidate_options:
                assert(result[overr_option.key].can_override)
                result[overr_option.key].value = candidate_options[0].value

        return result

    def set_user(self, user):
        ''' 
        Customizes configuration for given user.
        
        If user is None ~~> see __init__ method.
        '''
        
        self.user = user
        self._fill_cache()
    
    def _fill_cache(self):
        ''' Fills cache with values from db. If user is not set, then cache is empty. '''
        if self.user:
            self._cached_data = self.get_all_key_value_options()
        else:
            self._cached_data = {}
        
    def clear(self, truncate_config=False, truncate_userconfig=False):
        ''' 
        Clears cache and optionally models.
        
        If truncate_config is True, removes all data from Configuration model AND UserConfiguration model.
        If truncate_config is False and truncate_userconfig is True, then user's records 
        from UserConfiguration are removed.
        '''
        self._cached_data = {}
        if truncate_config:
            UserConfiguration.objects.all().delete()
            Configuration.objects.all().delete()
        if truncate_userconfig:
            UserConfiguration.objects.filter(user=self.user).delete()

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
                result, created = UserConfiguration.objects.get_or_create(option=config_option, user=self.user, 
                                                                          defaults={'user': self.user, 'value': value})
                result.value = value
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

    def set_can_override(self, key, can_override):
        '''
        Sets whether key can be overriden.
        '''
        try:
            option = Configuration.objects.get(key=key)
        except Configuration.DoesNotExist, e:
            raise Configuration.DoesNotExist(e.args + (key,))
        else:
            option.can_override = can_override
            option.save()
            
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
        else:
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
    def as_str(self, value):
        return unicode(value)
        
    def get_str(self, key):
        '''
        Returns unicode string associated with given key.
        Raises Configuration.DoesNotExist if key isn't found.
        '''
        return self.as_str(self.__getitem__(key))

    def set_str(self, key, value):
        value = unicode(value)
        self.__setitem__(key, value)
    
    # int
    def as_int(self, value):
        return int(value)
    
    def get_int(self, key):
        '''
        Returns integer associated with given key.
        Raises Configuration.DoesNotExist if key isn't found.
        Raises ValueError iff int(key) does.
        '''
        return self.as_int(self.__getitem__(key))

    def set_int(self, key, value):
        '''
        Associates integer value with key.
        Raises ValueError iff int(key) does.
        '''
        value = int(value)
        self.__setitem__(key, value)

    # bool
    def as_bool(self, value):
        return value == Config._true_value
        
    def get_bool(self, key):
        '''
        Returns True or False - legal bool value, neither 'True' nor '1'.
        Raises Configuration.DoesNotExist if key isn't found.
        '''
        value = self.__getitem__(key)
        assert(value in [Config._true_value, Config._false_value])
        return self.as_bool(value)

    def set_bool(self, key, value):
        value = bool(value)
        self.__setitem__(key, value)

    # list
    def as_list(self, value):
        return json.loads(value)
    
    def get_list(self, key):
        '''
        Returns list.
        Raises Configuration.DoesNotExist if key isn't found.
        Raises ValueError if value associated with key is not a list.
        '''
        value = self.__getitem__(key)
        return self.as_list(value)

    def set_list(self, key, value):
        '''
        Associates list with given key.
        Raises ValueError if value associated with key is not a list.
        '''
        value = list(value)
        self.__setitem__(key, value)   # json.dumps is done in __setitem__
