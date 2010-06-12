# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import Group, User
from baseapp.models import Book, BookRequest
# from baseapp.models import CustomUser
from config import Config

attrs_dict = { 'class': 'required' }

# see http://code.google.com/p/django-registration/source/browse/trunk/registration/forms.py


class BookRequestForm(forms.Form):
    '''
    Form for requesting book. Users can add their propositions of books,
    they would like to have in the library.
    '''
    def _books_choice_list():
        na = (0, '-- not applicable --')
        return [na] + [(b.id,b.title) for b in Book.objects.all().order_by('title')]

    book = forms.ChoiceField(choices=_books_choice_list(), label="Book")

    info = forms.CharField(widget=forms.Textarea,
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
        # field exists at all
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
        if 'info' in self.cleaned_data:
            print self.cleaned_data['info']
            info_len = len(self.cleaned_data['info'])
            if info_len < min_info_len:
                raise forms.ValidationError(u'Your request is too short. Should be at least %d, but was %d' % (min_info_len, info_len))
            return self.cleaned_data
        raise forms.ValidationError(u"Your request doesn't contain any informations. Should be at least %d long" % (min_info_len,))

    def save(self):
        info = self.cleaned_data['info']
        book_id = int(self.cleaned_data['book']) if self.cleaned_data['book'] != '0' else None
        book = Book.objects.get(pk=book_id)
        req = BookRequest(who=self.user, info=info, book=book)
        req.save()


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
                # TODO this should be reported
                # log_warning(msg)
        # save
        user.save()
        return user
