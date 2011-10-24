# -*- coding: utf-8 -*-

from entelib.baseapp.models import Configuration, UserConfiguration, ConfigurationValueType
from baseapp.utils import get_logger
from django.contrib.auth.models import Group

# where is json?
try:
    from django.utils import simplejson as json
except ImportError:
    try:
        import json
    except ImportError:
        try:
            import simplejson as json
        except ImportError:
            raise


class ConfigValueTypeHelper(object):

    def __init__(self):
        self.logger = get_logger('config')
        self.supported_types = ['int', 'bool', 'unicode', 'list_groupnames']

    def get_parsers(self):
        '''
        Returns dict of parsers, which convert string value (i.e. from form input) to proper type.

        Returns:
            { typename : {  'parse_fun' : any_parsing_function,
                            'error_msg' : message_displayed_if_parsing_fails,
                         }
             ...
            }
        parse_fun is mandatory
        error_msg is optional. If not given, message from parse_fun will be used.
        '''
        def parse_list_of_groupnames(names):
            """
            Returns list of group names. If any of names doesn't name a group, ValueError will be raised.
            Exception will be raised only for first 'fake' name.
            Args:
                names -- list of group names as string.
            """
            from django.contrib.auth.models import Group
            names = names.replace("u'", '').replace('u"', '')    # naive method of parsing. How to do it better?
            names = names.replace('"', '').replace("'", '')
            names = names.replace('[', '').replace("]", '')
            list_of_names = names.split(',')
            list_of_names = [name.strip() for name in list_of_names]
            for name in list_of_names:
                try:
                    Group.objects.get(name=name)
                except Group.DoesNotExist:
                    raise ValueError("Group `%s` wasn't found" % name)
            return list_of_names

        parse_fun = 'parse_fun'
        error_msg = 'error_msg'
        parsers = {
            'int' :
                {parse_fun  : lambda x: int(x),
                 error_msg  : 'Expected integer',
                },
            'bool':
                {parse_fun : lambda x: x=='True',  # see also definition in get_form_widget_for_type below
                 error_msg : 'Expected boolean',
                },
            'unicode':
                {parse_fun : lambda x: unicode(x),
                },
            'list_groupnames':
                {parse_fun : parse_list_of_groupnames,
                },
            }

        # cut parsers for unsupported types
        supported_parsers = {}
        for type, parser in parsers.items():
            if type in self.supported_types:
                supported_parsers[type] = parser
        return supported_parsers

    def get_form_widget_for_type(self, typename):
        from django import forms
        default_widget = forms.CharField(required=True, widget=forms.Textarea)
        widgets = {
            'int'    : forms.IntegerField(required=True),
#             'bool'   : forms.BooleanField(required=False),
            'bool'   : forms.ChoiceField(choices=(('True','True'),('False','False')), required=True),
            'unicode': forms.CharField(required=True, widget=forms.Textarea),
            'list_groupnames': forms.CharField(required=True, widget=forms.Textarea),
            }

        # cut widgets for unsupported types
        supported_widgets = {}
        for type, widget in widgets.items():
            if type in self.supported_types:
                supported_widgets[type] = widget

        # return widget
        if typename not in supported_widgets:
            widget = default_widget
            self.logger.error('Widget for typename `%s` was not found. Default is used.' % typename)
        else:
            widget = supported_widgets[typename]
        return widget

    def is_value_of_type(self, value, type):
        '''
        Args:
            type -- str. ConfigurationValueType is not officially supported.
        '''
        if isinstance(type, ConfigurationValueType):
            type = type.name
        if type not in self.supported_types:
            self.logger.error('Type `%s` is not supported. Requested value: `%s`.' % (type, value))
            return False
        if type == 'int':
            return isinstance(value, int)
        elif type == 'bool':
            return isinstance(value, bool)
        elif type == 'unicode':
            return isinstance(value, basestring)
        elif type == 'list_groupnames':
            result = isinstance(value, list)
            # return result
            for groupname in value:
                try:
                    Group.objects.get(name=groupname)
                except Group.DoesNotExist:
                    msg = "Group for name `%s` doesn't exist" % groupname
                    self.logger.error(msg)
                    return False
            return result
        else:
            self.logger.error("Couldn't verify value `%s` against type `%s`" % (value, type))
            return False


class Config(object):
    '''
    Accesses configuration stored in database.
    '''

    class Option(object):
        def __init__(self, key, type, user_value, global_value, description, can_override):
            '''
            Args:
                key -- str.
                type -- instance of ConfigurationValueType.
                user_value -- serialized value defined per user. Can be None.
                global_value -- serialized value defined not per user. Cannot be None.

            Extra fields:
                value -- *deserialized* value associated with key. Value of global_value or user_value,
                         respectively to can_override.
                         If user_value is None, then value == global_value.
            '''
            self.logger = get_logger('config.option')
            assert isinstance(key, basestring)
            assert isinstance(type, ConfigurationValueType)
            assert isinstance(can_override, bool)
            assert global_value

            self.key = key
            self.type = type
            self.user_value = Config.Option.deserialize(user_value, self.type)
            self.global_value = Config.Option.deserialize(global_value, self.type)
            if can_override and (self.user_value is not None):
                self.value = self.user_value
            else:
                self.value = self.global_value
            self.can_override = can_override
            self.description = description

        def __unicode__(self):
            return u'%s %s %s' % (self.can_override, self.key, self.value)

        @staticmethod
        def is_value_of_type(value, type):
            '''
            Returns True of False.
            '''
            return ConfigValueTypeHelper().is_value_of_type(value, type)

        @staticmethod
        def serialize(value, type):
            if not Config.Option.is_value_of_type(value, type):
                raise ValueError('Invalid value of type `%s`: `%s`' % (type, repr(value)))
            ser_value = json.dumps(value)
            return ser_value

        @staticmethod
        def deserialize(value, type):
            if value is None:
                return None
            deser_value = json.loads(value)
            if not Config.Option.is_value_of_type(deser_value, type):
                raise ValueError('Invalid value of type `%s`: `%s`' % (type, repr(deser_value)))
            return deser_value

    class KeyDoesNotExist(KeyError):
        pass

    class KeyCannotBeOverrided(Exception):
        pass

    def __init__(self, user=None, validators={}):
        '''
        user is one for whom configuration will be customized.

        NOTE:
            User can be None only if you want to register new values in Configuration (NOT 'per user configuration').
            Usages other than that can be unpredictable in effects.
        '''
        self._cached_data = {}
        self.set_user(user)

    def set_user(self, user):
        '''
        Customizes configuration for given user.

        If user is None ~~> see __init__ method.
        '''
        self.user = user
        self._fill_cache()

    def _fill_cache(self):
        '''
        Fills cache with values from db. If user is not set, then cache is empty.
        Cache is empty because one may create global Config instance and user set later.
        '''
        if self.user:
#            self._cached_data = self.get_all_key_value_options()
            self._cached_data = self.get_all_options()
        else:
            self._cached_data = self.get_global_options()

    def clear(self, truncate_config=False, truncate_userconfig=False, truncate_types=False):
        '''
        Clears cache and optionally models.

        Args:
            truncate_config -- If True, removes all data from all Configuration, ConfigurationValueType
                               AND UserConfiguration models.
                               If False and truncate_userconfig is True, then user's records from
                               UserConfiguration are removed.
            truncate_userconfig -- If True, UserConfiguration model will be cleared.
                              WARNING: take care of referential actions (like CASCADE...)
            truncate_types -- If True, then ConfigurationValueType will be cleared.
                              WARNING: take care of referential actions (like CASCADE...)
        '''
        self._cached_data = {}
        if truncate_config:
            # NOTE: order is important, because of referential actions.
            UserConfiguration.objects.all().delete()
            Configuration.objects.all().delete()
            ConfigurationValueType.objects.all().delete()
        if truncate_userconfig:
            UserConfiguration.objects.filter(user=self.user).delete()
        if truncate_types:
            ConfigurationValueType.objects.all().delete()

    def __getitem__(self, key):
        '''
        Returns value for key. Value is deserialized.

        Raises:
            Configuration.DoesNotExist, if key is not found.
        '''
        if key == 'min_days_left_to_enable_prolongation':
            return 7
        if key == 'max_prolongation_days':
            return 30

        return self.get_option(key).value

    def get_option(self, key):
        '''
        Returns Config.Option instance associated with key.

        Raises:
            Configuration.DoesNotExist, if key is not found.
        '''
        if key in self._cached_data:
            return self._cached_data[key]
        else:
            # look for key, if it exists at all
            try:
                Configuration.objects.get(key=key)
            except Configuration.DoesNotExist, e:
                raise Configuration.DoesNotExist(e.args + (key,))
            # now we know that key is there
            self._fill_cache()
            assert key in self._cached_data, self._cached_data
            return self._cached_data[key]

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

    def get_global_options(self):
        '''
        Returns dict of options with only global values.
        '''
        options = list(Configuration.objects.select_related().all())
        result = {}
        for opt in options:
            option = Config.Option(key = opt.key,
                                   global_value = opt.value,
                                   user_value = None,
                                   type = opt.type,
                                   can_override = opt.can_override,
                                   description = opt.description)
            result[opt.key] = option
        return result

    def get_all_options(self):
        '''
        Gets all config options and returns it as a dict of Config.Option records -- { key: option }
        If self.user is None, then works the same as get_global_options().
        '''
        if not self.user:
            return self.get_global_options()

        result = self.get_global_options()
        user_options = UserConfiguration.objects.select_related('option').filter(user=self.user)

        for uopt in user_options:
            user_value = None
            if uopt.option.can_override:
                user_value = uopt.value
            option = Config.Option(key          = uopt.option.key,
                                   global_value = uopt.option.value,
                                   user_value   = user_value,
                                   type         = uopt.option.type,
                                   can_override = uopt.option.can_override,
                                   description  = uopt.option.description)
            result[option.key] = option
        return result

    def insert_or_update_global(self, key, value, type, description, can_override):
        '''
        Args:
            key -- string
            value -- mixed
            type -- instance of ConfigurationValueType
            description -- string
            can_override -- bool
        '''
        assert isinstance(type, ConfigurationValueType)
        value_str = Config.Option.serialize(value, type)
        try:
            option = Configuration.objects.get(key=key)
        except Configuration.DoesNotExist:
            # insert
            option = Configuration(key=key, value=value_str, description=description, type=type, can_override=can_override)
            option.save()
        else:
            # update
            option.value = value_str
            option.type = type
            option.description = description
            option.can_override = can_override
            option.save()
            del self._cached_data[key]

    def set_global_value(self, key, value):
        '''
        Sets global value for key. Key must exist.
        Global means not per user.

        Raises:
            Configuration.DoesNotExist, if key is not found.
        '''
        assert (key in self)
        config_option = Configuration.objects.get(key=key)
        config_option.value = Config.Option.serialize(value, config_option.type)
        config_option.save()

        del self._cached_data[key]

    def __setitem__(self, key, value):
        '''
        Sets value of key.

        It properly reveals types of value given if it (value's type) is one of following:
        boolean, int, string, list.

        May raise Config.KeyCannotBeOverrided if one tries to violate this. Can be checked with
        config.can_override method - check it's description for more details.
        '''
        # check if overriding is possible. This function allows to create
        # options and then overriding shouldn't be checked
        if (key in self) and (not self.can_override(key)):
            raise Config.KeyCannotBeOverrided

        # reveal how value should be stored in model
#        value = self._value_to_repr(value)
        type_of_value = self.get_type(key)
        value = Config.Option.serialize(value, type_of_value)

        # insert new key, value pair
        if key not in self:
            raise Exception('Keys cannot be inserted via __setitem__')
#            record = Configuration(key=key, value=value, type=type_of_value, description='')
#            record.save()
        # update value
        else:
            can_override = self.can_override(key, silent=False)
            if self.user and can_override:
                config_option = Configuration.objects.get(key=key)
                result, created = UserConfiguration.objects.get_or_create(option=config_option, user=self.user,
                                                                          defaults={'user': self.user, 'value': value})
                result.value = value
                result.save()

        # invalidate cache
        del self._cached_data[key]

    def __contains__(self, key):
        ''' Checks if item is in configuration. Returns True or False. '''
        try:
            self.__getitem__(key)
            return True
        except Configuration.DoesNotExist:
            return False

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
            option = Configuration.objects.only('can_override', 'key').get(key=key)
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

    # type
    def get_type(self, key):
        '''
        Returns type of value associated with key.

        Args:
            key -- str
        '''
        try:
            result = Configuration.objects.select_related().get(key=key)
        except Configuration.DoesNotExist, e:
            raise Configuration.DoesNotExist(e.args + (key,))
        else:
            return result.type

    def set_type(self, key, type):
        '''
        Sets type for value for given key.
        Args:
            key -- str
            type -- instance of ConfigurationValueType
        '''
        assert isinstance(type, ConfigurationValueType)
        try:
            result = Configuration.objects.get(key=key)
        except Configuration.DoesNotExist, e:
            raise Configuration.DoesNotExist(e.args + (key,))
        else:
            result.type = type
            result.save()

    # description
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

    def get_description(self, key):
        '''
        Gets description of given key.
        '''
        try:
            result = Configuration.objects.get(key=key)
        except Configuration.DoesNotExist, e:
            raise Configuration.DoesNotExist(e.args + (key,))
        return result.description

    def get_str(self, key):
        return self[key]
    def get_int(self, key):
        return self[key]
    def get_bool(self, key):
        return self[key]
    def get_list(self, key):
        return self[key]

    def set_str(self, key, value):
        self[key] = value
    def set_int(self, key, value):
        self[key] = value
    def set_bool(self, key, value):
        self[key] = value
    def set_list(self, key, value):
        self[key] = value

#    # str
#    def as_str(self, value):
#        return unicode(value)
#
#    def get_str(self, key):
#        '''
#        Returns unicode string associated with given key.
#        Raises Configuration.DoesNotExist if key isn't found.
#        '''
#        return self.as_str(self.__getitem__(key))
#
#    def set_str(self, key, value):
#        value = unicode(value)
#        self.__setitem__(key, value)
#
#    # int
#    def as_int(self, value):
#        return int(value)
#
#    def get_int(self, key):
#        '''
#        Returns integer associated with given key.
#        Raises Configuration.DoesNotExist if key isn't found.
#        Raises ValueError iff int(key) does.
#        '''
#        return self.as_int(self.__getitem__(key))
#
#    def set_int(self, key, value):
#        '''
#        Associates integer value with key.
#        Raises ValueError iff int(key) does.
#        '''
#        value = int(value)
#        self.__setitem__(key, value)
#
#    # bool
#    def as_bool(self, value):
#        return value == Config._true_value
#
#    def get_bool(self, key):
#        '''
#        Returns True or False - legal bool value, neither 'True' nor '1'.
#        Raises Configuration.DoesNotExist if key isn't found.
#        '''
#        value = self.__getitem__(key)
#        assert(value in [Config._true_value, Config._false_value])
#        return self.as_bool(value)
#
#    def set_bool(self, key, value):
#        value = bool(value)
#        self.__setitem__(key, value)
#
#    # list
#    def as_list(self, value):
#        return json.loads(value)
#
#    def get_list(self, key):
#        '''
#        Returns list.
#        Raises Configuration.DoesNotExist if key isn't found.
#        Raises ValueError if value associated with key is not a list.
#        '''
#        value = self.__getitem__(key)
#        return self.as_list(value)
#
#    def set_list(self, key, value):
#        '''
#        Associates list with given key.
#        Raises ValueError if value associated with key is not a list.
#        '''
#        value = list(value)
#        self.__setitem__(key, value)   # json.dumps is done in __setitem__


