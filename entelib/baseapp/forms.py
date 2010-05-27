# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import Group, User
# from baseapp.models import CustomUser
from config import Config

attrs_dict = { 'class': 'required' }

# see http://code.google.com/p/django-registration/source/browse/trunk/registration/forms.py


class ProfileEditForm(forms.Form):
    '''
    Form for editing user profile.
    User can edit their both email and password.
    The new password must be entered twice in order to catch typos.

    Empty field = no edition.
    '''
    current_password = forms.CharField(widget=forms.PasswordInput(render_value=False),
        label=(u'Current password'), required=False)
    email = forms.EmailField(label=(u'New email'), required=False)
    password1 = forms.CharField(widget=forms.PasswordInput(render_value=False),
        label=(u'New password'), required=False)
    password2 = forms.CharField(widget=forms.PasswordInput(render_value=False),
        label=(u'New password (again)'), required=False)


    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ProfileEditForm, self).__init__(*args, **kwargs)


    def clean_current_password(self):
        '''
        Verify that the password user typed as their current one is correct.
        '''
        if not 'current_password' in self.cleaned_data:
            return self.cleaned_data
        if not self.user.check_password(self.cleaned_data['current_password']):
            raise forms.ValidationError(u'The password is incorrect.')
        return self.cleaned_data


    def clean(self):
        '''
        Verify that the values typed into the new password fields match.
        '''
        if not ('password1' in self.cleaned_data and 'password2' in self.cleaned_data):
            return self.cleaned_data
        if self.cleaned_data['password1'] != self.cleaned_data['password2']:
            raise forms.ValidationError(u'You must type the same new password each time.')
        return self.cleaned_data


    def save(self):
        '''
        Edit user profile.
        '''
        if self.cleaned_data['email'] != '':
            new_email = self.cleaned_data['email']
            self.user.email = new_email
        if self.cleaned_data['password1'] != '':
            self.user.set_password(self.cleaned_data['password1'])
        self.user.save()
        return self.user


class RegistrationForm(forms.Form):
    '''
    Form for registering a new user account.

    Validates that the requested username is not already in use, and
    requires the password to be entered twice to catch typos.

    Subclasses should feel free to add any additional validation they need, but should
    either preserve the base ``save()``
    '''
    username = forms.RegexField(regex=r'^\w+$',
                                min_length=3,
                                max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=(u'Username'),
                                help_text=r'Can contain only alphanumeric values or underscores. Length should be at least 3.'
                                )
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
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(u'This username is already taken. Please choose another.')


    def clean(self):
        '''
        Verifiy that the values entered into the two password fields match.
        Note that an error here will end up in ``non_field_errors()`` because
        it doesn't apply to a single field.
        '''
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
        user.save()   # checkpoint save, because cfg.get_list may throw and is_active is True as default

        # add user to default groups
        cfg = Config()
        groups = cfg.get_list('user_after_registration_groups')
        print groups
        for group_name in groups:
            try:
                g = Group.objects.get(name=group_name)
                user.groups.add(g)
            except Group.DoesNotExist, e:
                msg = u'Adding user %s to group %s failed. Group not found.' % (user.username, group_name)
                # TODO this should be reported
                # log_warning(msg)
        # save
        user.save()
        return user
