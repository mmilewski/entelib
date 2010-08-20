# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import Group, User
from baseapp.models import Book, BookRequest, Building, PhoneType, Phone,\
    Location, BookCopy, Category, Author
# from baseapp.models import CustomUser
from config import Config
from baseapp.utils import pprint
import baseapp.utils as utils
from copy import copy
from baseapp.views_aux import get_phones_for_user
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import ModelForm
from django.db.models.query_utils import Q
import models_config as CFG
from baseapp.config import ConfigValueTypeHelper

attrs_dict = { 'class': 'required' }



class ConfigOptionEditForm(forms.Form):
    '''
    Form for editing config's option.
    '''
    value        = forms.CharField(required=True, widget=forms.Textarea)
    can_override = forms.BooleanField(required=False)
    description  = forms.CharField(required=False, widget=forms.Textarea, max_length=CFG.configuration_descirption_len)
        
    def __init__(self, user, option_key, config, is_global, *args, **kwargs):
        super(ConfigOptionEditForm, self).__init__(*args, **kwargs)
        self.user = user
        self.option_key = option_key
        self.is_global = is_global
        self.config = config
        type = self.config.get_type(self.option_key)
        self.fields['value'] = ConfigValueTypeHelper().get_form_widget_for_type(type.name)

    def clean_description(self):
        if self.is_global:
            if len(self.cleaned_data['description']) < 2:
                raise forms.ValidationError('Description cannot be empty')
            return self.cleaned_data['description']
        else:
            return ''

    def clean_value(self):
        if not 'value' in self.cleaned_data:
            raise forms.ValidationError(u'Value must have any value')
        config = self.config
        value = self.cleaned_data['value']
        type = config.get_type(self.option_key)

        parsers = ConfigValueTypeHelper().get_parsers()
        
        for typename, v in parsers.items():
            if type.name == typename:
                try:
                    cast_value = v['parse_fun'](value)
                except ValueError, e:
                    if 'error_msg' in v:
                        msg = v['error_msg']
                    else:
                        msg = unicode(e)
                    raise forms.ValidationError(msg)
                else:
                    return cast_value
        else:
            raise forms.ValidationError('Unable to verify type. Please contact admin or developer.')
        return value

    def clean(self):
        config = self.config
        key = self.option_key
        is_global = self.is_global
        if not is_global:
            if not config.can_override(key):
                raise forms.ValidationError(u"Key %s cannot be overriden" % (key,))
        else:
            pass
        return self.cleaned_data

    def save(self):
        key = self.option_key
        config = self.config
        if self.is_global:
            config.set_global_value(key, self.cleaned_data['value'])
            config.set_can_override(key, self.cleaned_data['can_override'])
            config.set_description(key, self.cleaned_data['description'])
        else:
            config[key] = self.cleaned_data['value']


class BookRequestForm(forms.Form):
    '''
    Form for requesting book. Users can add their propositions of books,
    they would like to have in the library.

    see:  http://code.google.com/p/django-registration/source/browse/trunk/registration/forms.py
    '''
    def _books_choice_list():
        na = (0, '-- not applicable --')
        return [na] + [(b.id,b.title) for b in Book.objects.all().order_by('title')]

    book = forms.ChoiceField(choices=_books_choice_list(), label="Book")
    info = forms.CharField(widget=forms.Textarea(attrs={'cols': 90, 'rows': 16}),
                           label=(u'Information about book you request'),
                           required=True,
                           )


    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(BookRequestForm, self).__init__(*args, **kwargs)

    def clean_info(self):
        if not 'info' in self.cleaned_data:
            raise forms.ValidationError(u'Give any informations about book.')
        return self.cleaned_data['info']

    def clean_book(self):
        # field doesn't exist at all
        if not 'book' in self.cleaned_data:
            raise forms.ValidationError(u"Form data corrupted. Book field wasn't found.")
        # id==0 is a special case - but it's correct
        book_id = (int)(self.cleaned_data['book'])
        if book_id == 0:
            return self.cleaned_data['book']
        # check if one tries to corrupt db.
        try:
            Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            raise forms.ValidationError(u"Corrupted book's id")
        return self.cleaned_data['book']

    def clean(self):
        config = Config()
        min_info_len = config.get_int('book_request_info_min_len')
        assert isinstance(min_info_len, int)
        if 'info' in self.cleaned_data:
            info_len = len(self.cleaned_data['info'])
            if info_len < min_info_len:
                raise forms.ValidationError(u'Your request is too short. Should be at least %d characters long, but was %d.' % (min_info_len, info_len))
            return self.cleaned_data
        raise forms.ValidationError(u"Your request doesn't contain any information. It should be at least %d characters long." % (min_info_len,))

    def save(self):
        info = self.cleaned_data['info']
        book_id = int(self.cleaned_data['book']) if self.cleaned_data['book'] != '0' else None
        book = Book.objects.get(pk=book_id) if book_id else None
        req = BookRequest(who=self.user, info=info, book=book)
        req.save()


class ProfileEditChoiceList:
    @staticmethod
    def buildings():
        ''' Builds list od 2-tuples containing Buildings. '''
        choice_list =  [ (0, u'--- not specified ---')]
        choice_list += [(b.id, b.name)  for b in Building.objects.order_by('name').all()] 
        return choice_list

    @staticmethod
    def phone_types():
        ''' Builds list of 2-tuples containing PhoneTypes. '''
        return [(pt.id, pt.name) for pt in PhoneType.objects.order_by('name').all()]
    
class ProfileEditForm(forms.Form):
    '''
    Form for editing user profile.
    User can edit their both email and password.
    The new password must be entered twice in order to catch typos.

    Empty field = no edition.
    '''

    phone_prefix = 'phone'
    phone_type_prefix = phone_prefix + 'Type'
    phone_value_prefix = phone_prefix + 'Value'
    
    username = forms.CharField(help_text=u'Required. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters', max_length=30, label=u'Username')
    first_name = forms.CharField(max_length=30, required=False, label=u'First name')
    last_name = forms.CharField(max_length=30, required=False, label=u'Last name')
    email = forms.EmailField(label=(u'E-mail'), required=False)
    work_building = forms.ChoiceField(choices=ProfileEditChoiceList.buildings(), label="Building I work in")

    phoneType0 = forms.ChoiceField(choices=ProfileEditChoiceList.phone_types(), label='Phone 0', required=False)
    phoneValue0 = forms.CharField(label='', required=False)

    phoneType1 = forms.ChoiceField(choices=ProfileEditChoiceList.phone_types(), label='Phone 1', required=False)
    phoneValue1 = forms.CharField(label='', required=False)

    phoneType2 = forms.ChoiceField(choices=ProfileEditChoiceList.phone_types(), label='Phone 2', required=False)
    phoneValue2 = forms.CharField(label='', required=False)

    phoneType3 = forms.ChoiceField(choices=ProfileEditChoiceList.phone_types(), label='Phone 3', required=False)
    phoneValue3 = forms.CharField(label='', required=False)

    phoneType4 = forms.ChoiceField(choices=ProfileEditChoiceList.phone_types(), label='Phone 4', required=False)
    phoneValue4 = forms.CharField(label='', required=False)

    current_password = forms.CharField(widget=forms.PasswordInput(render_value=False),
        label=(u'Your password'), required=True)
    password1 = forms.CharField(widget=forms.PasswordInput(render_value=False),
        label=(u'New password'), required=False)
    password2 = forms.CharField(widget=forms.PasswordInput(render_value=False),
        label=(u'New password (again)'), required=False)



    def __init__(self, profile_owner, editor=None, *args, **kwargs):
        '''
        profile_owner is instance of User, whose profile will be changed.
        editor is instance of User, who will change the profile.
        
        If editor is None, then it is set to profile_owner
        '''
        if editor:
            self.editor = editor
        else:
            self.editor = profile_owner
        self.profile_owner = profile_owner
        super(ProfileEditForm, self).__init__(*args, **kwargs)
        # only admin can edit username, first name and last name
        if not self.editor.has_perm('baseapp.edit_xname'):
            self.fields['username'].widget.attrs['readonly'] = True
            self.fields['first_name'].widget.attrs['readonly'] = True
            self.fields['last_name'].widget.attrs['readonly'] = True


    def clean(self):
        '''
        Check if passwords matches (these are 'new password' and 'again new password')
        '''
        if not ('password1' in self.cleaned_data and 'password2' in self.cleaned_data):
            return self.cleaned_data
        if self.cleaned_data['password1'] != self.cleaned_data['password2']:
            raise forms.ValidationError(u'You must type the same new password each time.')
        return self.cleaned_data


    def clean_current_password(self):
        '''
        Verify that the password user typed as their current one is correct.
        '''
        if not 'current_password' in self.cleaned_data:
            return self.cleaned_data
        if not self.editor.check_password(self.cleaned_data['current_password']):
            raise forms.ValidationError(u'The password is incorrect.')
        return self.cleaned_data
    
    
    def clean_first_name(self):
        # exit if unchanged
        if self.profile_owner.first_name == self.cleaned_data['first_name']:
            return self.profile_owner.first_name
        # check perms
        if not self.editor.has_perm('baseapp.edit_xname'):
            raise forms.ValidationError("You don't have permissions to edit first name")

        value = self.cleaned_data['first_name']
        if len(value) > 30:
            raise forms.ValidationError('Too long')
        return value
    
    def clean_last_name(self):
        # exit if unchanged
        if self.profile_owner.last_name == self.cleaned_data['last_name']:
            return self.profile_owner.last_name
        # check perms
        if not self.editor.has_perm('baseapp.edit_xname'):
            raise forms.ValidationError("You don't have permissions to edit last name")

        value = self.cleaned_data['last_name']
        if len(value) > 30:
            raise forms.ValidationError('Too long')
        return value
        
    def clean_username(self):
        # exit if unchanged
        if self.profile_owner.username == self.cleaned_data['username']:
            return self.profile_owner.username
        # check perms
        if not self.editor.has_perm('baseapp.edit_xname'):
            raise forms.ValidationError("You don't have permissions to edit username")

        value = self.cleaned_data['username']
        try:
            threatened_user = User.objects.get(username=value)
        except ObjectDoesNotExist:
            pass
        else:
            if threatened_user.id != self.profile_owner.id:
                raise forms.ValidationError('User %s already exists!' % value)
        if len(value) > 30:
            raise forms.ValidationError('Too long')
        return value
    
    def clean_phone_type(self, key_name):
        data = self.cleaned_data
        return data[key_name] if key_name in data else ''

    def clean_phone_value(self, key_name):
        data = self.cleaned_data
        return data[key_name].strip() if key_name in data else ''
 
    def clean_phoneType0(self):
        return self.clean_phone_type('phoneType0')
        
    def clean_phoneType1(self):
        return self.clean_phone_type('phoneType1')
        
    def clean_phoneType2(self):
        return self.clean_phone_type('phoneType2')
        
    def clean_phoneType3(self):
        return self.clean_phone_type('phoneType3')
        
    def clean_phoneType4(self):
        return self.clean_phone_type('phoneType4')

    def clean_phoneValue0(self):
        return self.clean_phone_value('phoneValue0')

    def clean_phoneValue1(self):
        return self.clean_phone_value('phoneValue1')

    def clean_phoneValue2(self):
        return self.clean_phone_value('phoneValue2')

    def clean_phoneValue3(self):
        return self.clean_phone_value('phoneValue3')

    def clean_phoneValue4(self):
        return self.clean_phone_value('phoneValue4')


    def get_cleaned_phones(self, cleaned_data):
        '''
        Gets info dealing with phones from cleaned_data. So returns a subset (subdictionary :>)
        of cleaned_data
        '''
        cleaned_phones = {}
        for k, v in cleaned_data.items():
            if k.startswith(self.phone_prefix):
                if k.startswith(self.phone_type_prefix):
                    v = int(v)
                cleaned_phones[k] = v
        return cleaned_phones


    def transform_cleaned_phones_to_list_of_phones(self, cleaned_phones):
        ''' 
        Transforms cleaned_phones dict to list of pairs: (phone_type, phone_value) -- both of these values 
        must exists. 
        
        Elements without it's pair will be omitted in result.
        
        If element's value after striping is empty, then related key will be omitted in result. 
        '''
        phones = []
        for i in range(len(cleaned_phones)):                 # this range is a bit (at most twice) too wide, but it doesn't hurt permormance
            type_pref = self.phone_type_prefix + str(i)
            value_pref = self.phone_value_prefix + str(i)
            if (type_pref in cleaned_phones) and (value_pref in cleaned_phones):
                if cleaned_phones[value_pref].strip():                             # don't allow empty entries
                    phones.append( (cleaned_phones[type_pref], cleaned_phones[value_pref]) )
        return phones


    def extract_phones_to_add(self, user_phones, sent_phones):
        '''
        Desc:
            Using sets language: it returns sent_phones\user_phones (where '\' means sets difference) 
            -- these are phones to be added to user's profile.
    
        Args:
            user_phones -- list of Phone instances. Can be obtained from user profile.
            sent_phones -- list of 2-tuples (phone_type_id, phone_value). Can be obtained
                           from self.transform_cleaned_phones_to_list_of_phones()
        
        Return:
            List of 2-tuples: (phone_type_id, phone_value)
        '''
        phones_to_add = copy(sent_phones)
        for user_phone in user_phones:
            phone_tuple = (user_phone.type.id, user_phone.value)
            if phone_tuple in phones_to_add:        # if phone is not new
                phones_to_add.remove(phone_tuple)
        return phones_to_add


    def extract_phones_to_remove(self, user_phones, sent_phones):
        '''
        Desc:
            Returns user_phone\sent_phones, using sets language 
            -- these are phones to be removed from user's profile.

        Args:
            user_phones -- list of Phone instances. Can be obtained from user profile.
            sent_phones -- list of 2-tuples (phone_type_id, phone_value). Can be obtained
                           from self.transform_cleaned_phones_to_list_of_phones()
        
        Return:
            List of 2-tuples: (phone_type_id, phone_value)
        '''       
        phones_to_remove = []
        for user_phone in user_phones:
            phone_tuple = (user_phone.type.id, user_phone.value)
            if phone_tuple not in sent_phones:        # if phone is not new                
                phones_to_remove.append(phone_tuple)
        return phones_to_remove


    def add_phones_to_profile(self, phones_to_add):
        '''
        Desc:
            Adds phones from 2-tuple list to self.profile_owner's profile. 
            If a phone is already there, it will be duplicated.
        
        Args:
            phones_to_add -- list of 2-tuples (phone_type_id, phone_value). Can be 
                             obtained from self.extract_phones_to_add()
         '''
        user_profile = self.profile_owner.get_profile()
        for phone_type_id, phone_value in phones_to_add:
            new_phone = Phone(type=PhoneType.objects.get(id=phone_type_id),
                              value = phone_value)
            new_phone.save()
            user_profile.phone.add(new_phone)
        user_profile.save()


    def remove_phones_from_profile(self, phones_to_remove):
        '''
        Desc:
            Removes phones from self.profile_owner's profile.
        
        Args:
            phones_to_remove -- list of 2-tuples (phone_type_id, phone_value). Can be 
                                obtained from self.extract_phones_to_remove()
         '''
        user_profile = self.profile_owner.get_profile()
        user_phones = user_profile.phone.all()

        for usr_phone in user_phones:
            for rmv_phone in phones_to_remove:
                if usr_phone.type.id == rmv_phone[0] and usr_phone.value == rmv_phone[1]:
                    user_profile.phone.remove(usr_phone)
        user_profile.save()
        

    def save(self):
        '''
        Commit changes in user profile.
        Returns saved user
        '''
        if self.cleaned_data['email'] != '':
            new_email = self.cleaned_data['email']
            self.profile_owner.email = new_email
        if self.cleaned_data['password1'] != '':
            self.profile_owner.set_password(self.cleaned_data['password1'])
        if self.cleaned_data['work_building']:
            building_id = int(self.cleaned_data['work_building'])
            user_profile = self.profile_owner.get_profile()
            if building_id > 0:
                building = Building.objects.get(id=building_id)
                user_profile.building = building
            else:
                user_profile.building = None
            user_profile.save()
                
        self.profile_owner.first_name = self.cleaned_data['first_name']
        self.profile_owner.last_name = self.cleaned_data['last_name']

        # only admin can change usernames
        if self.editor.userprofile.is_admin():
            self.profile_owner.username = self.cleaned_data['username']

        cleaned_phones   = self.get_cleaned_phones(self.cleaned_data)
        phones_as_list   = self.transform_cleaned_phones_to_list_of_phones(cleaned_phones)        
        user_phones      = self.profile_owner.get_profile().phone.all()
        phones_to_add    = self.extract_phones_to_add(user_phones, phones_as_list)
        phones_to_remove = self.extract_phones_to_remove(user_phones, phones_as_list)

#        pprint('-------------------------- START save -------------------------------')
#        pprint(' --- cleaned_phones ---')
#        pprint(cleaned_phones)
#        pprint(' --- phones_as_list ---')
#        pprint(phones_as_list)
#        pprint(' --- user_phones ---')
#        pprint(user_phones)
#        pprint(' --- phones to add ---')
#        pprint(phones_to_add)
#        pprint(' --- phones to remove ---')
#        pprint(phones_to_remove)
#        pprint('-------------------------- END save -------------------------------')

        # removing must go first
        self.remove_phones_from_profile(phones_to_remove)
        self.add_phones_to_profile(phones_to_add)
        
        # uff, save & return
        self.profile_owner.save()
        return self.profile_owner
        
        
    @staticmethod
    def get_initials_for_user(user):
        ''' Returns initial fields values for specified user.'''
        # phones are list of 3-tuples: phone_type_id, phone_type, value
        phones = [ (p.type.id, p.type.name, p.value) for p in user.get_profile().phone.all() ]
        # initial values for phones
        phones_initial = {}
        for i, phone in enumerate(phones):
            phones_initial['phoneType'  + str(i)] = phone[0]    # type id
            phones_initial['phoneValue' + str(i)] = phone[2]    # value
    
        # prepare initial data
        form_initial = { 'first_name'  : user.first_name,
                         'last_name'   : user.last_name,
                         'username'    : user.username,
                         'email'       : user.email,
                        }
        form_initial.update(phones_initial)
        if user.get_profile().building:
            form_initial['work_building'] = user.get_profile().building.id
        
        return form_initial
    
    @staticmethod
    def build_default_context_for_user(user):
        ''' Returns default context for specified user.'''
        context = { 'first_name'   : user.first_name,
                    'last_name'    : user.last_name,
                    'user_id'      : user.id,
                    'email'        : user.email,
                    'building'     : user.get_profile().building,
                    'phones'       : get_phones_for_user(user),
                    # 'rentals'      : 'rentals/',         # moim zdaniem to jest _bardzo_ zle miejsce na te dane - przenioslem je do szablonu - mbr
                    # 'reservations' : 'reservations/',
                    }
        return context
                
                
class RegistrationForm(forms.Form):
    '''
    Form for registering a new user account.

    Validates that the requested username is not already in use, and
    requires the password to be entered twice to catch typos.

    Subclasses should feel free to add any additional validation they need, but should
    either preserve the base ``save()``
    '''
    # username = forms.RegexField(regex=r'^\w+$',
    #                             min_length=3,
    #                             max_length=30,
    #                             widget=forms.TextInput(attrs=attrs_dict),
    #                             label=(u'Username'),
    #                             help_text=r'Can contain only alphanumeric values or underscores. Length should be at least 3.'
    #                             )
    first_name = forms.CharField(max_length=30,
                                 widget=forms.TextInput(attrs=attrs_dict),
                                 label=(u'First name')
                                 )
    last_name = forms.CharField(max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=(u'Last name')
                                )
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=75)),
                             label=(u'Email'))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=(u'Password'))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=(u'Password (again)'))


    def clean_username(self):
        '''
        Validate that the username is alphanumeric and is not already in use.
        '''
        if ('first_name' not in self.cleaned_data) or ('last_name' not in self.cleaned_data):
            raise forms.ValidationError(u'First and last name must be given')
        username = self.cleaned_data['first_name'] + self.cleaned_data['last_name']
        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            self.cleaned_data['username'] = username
            return username
        else:
            raise forms.ValidationError(u'%s is already registered. Please contact administrator.' % username)


    def clean(self):
        '''
        Verifiy that the values entered into the two password fields match.
        Note that an error here will end up in ``non_field_errors()`` because
        it doesn't apply to a single field.
        '''
        self.clean_username()
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(u'You must type the same password each time.')
        return self.cleaned_data


    def save(self):
        '''
        Create the new user and returns it.
        '''
        user = User.objects.create_user(username = self.cleaned_data['username'],
                                        password = self.cleaned_data['password1'],
                                        email = self.cleaned_data['email']
                                        )
        user.is_active, user.is_superuser, user.is_staff = False, False, False
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()   # checkpoint save, because config.get_list may throw and is_active is True as default

        # add user to default groups
        config = Config()
        groups = config.get_list('user_after_registration_groups')
        for group_name in groups:
            try:
                g = Group.objects.get(name=group_name)
                user.groups.add(g)
            except Group.DoesNotExist, e:
                msg = u'Adding user %s to group %s failed. Group not found.' % (user.username, group_name)
                pprint(msg)
                # TODO this should be reported
                # log_warning(msg)
        # save
        user.save()
        return user


class LocationForm(ModelForm):   
    class Meta:
        model = Location
        fields = ('building', 'details', 'remarks', 'maintainer')

    groups = Group.objects.filter(Q(name='Librarians'))
    maintainer = forms.ModelMultipleChoiceField(User.objects.filter(groups__in=groups), required=False)


class BookForm(ModelForm):   
    class Meta:
        model = Book
        fields = ('title', 'category', 'author')

    author = forms.CharField(widget=forms.Textarea)
    category = forms.ModelMultipleChoiceField(Category.objects.all().order_by('name'))

    def clean_author(self):
        names_str = self.cleaned_data['author']
        name_list = utils.AutocompleteHelper(string=names_str).from_str()
        instances = []
        for name in name_list:
            authors = list(Author.objects.filter(name=name))
            if len(authors) < 1:
                raise forms.ValidationError("Name `%s` doesn't name any author" % name)
            else:
                instances.append(authors[0].id)
        return instances


class BookCopyForm(ModelForm):   
    class Meta:
        model = BookCopy
        # exclude = ('book',)

    def __init__(self, *args, **kwargs):
        super(BookCopyForm, self).__init__(*args, **kwargs)
        self.fields['book'].widget.attrs['readonly'] = True
        # self.fields['book'].widget.attrs['disabled'] = True
