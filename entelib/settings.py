# -*- coding: utf-8 -*-
# Django settings for entelib project.
import os
from os.path import abspath, dirname, join
PROJECT_PATH = dirname(abspath(__file__))

DEBUG = False
TEMPLATE_DEBUG = DEBUG

IS_DEV = False    # set to False if giving to users. This allows to disable some options (like admin panel or load default config)

# if True checks whether given password matches one in database.
CHECK_PASSWORD_ON_AUTH = True

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2' #, 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#DATABASE_NAME = 'database/database.db'      # Or path to database file if using sqlite3.
DATABASE_NAME = 'entelib'
DATABASE_USER = 'entelib'             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

EMAIL_HOST = 'mail.emea.nsn-intra.net'
EMAIL_PORT = 25

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Warsaw'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
#MEDIA_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'media')
MEDIA_ROOT = join(PROJECT_PATH,'media') + os.sep

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

PROJECT_NAME = 'entelib'
LOGIN_URL =  '/%s/login/' % PROJECT_NAME                # see http://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGOUT_URL = '/%s/logout/' % PROJECT_NAME
LOGIN_REDIRECT_URL = '/%s/' % PROJECT_NAME              # see http://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url


# Make this unique, and don't share it with anybody.
SECRET_KEY = 'c123x!_%j(ky=9c%_+9^s90znof2+juhy$-z(@pym(ls5(yxhb'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.common.CommonMiddleware',           # see DISALLOWED_USER_AGENTS, APPEND_SLASH, PREPEND_WWW
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.transaction.TransactionMiddleware',   # tie request-response to transaction
    'middleware-FeedbackMiddleware.FeedbackMiddleware',      # feedback handler
)

ROOT_URLCONF = 'entelib.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    join(PROJECT_PATH,'templates'),
    join(PROJECT_PATH,'email'),
)


TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
)


# message framework's settings
from django.contrib import messages
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
MESSAGE_LEVEL = messages.DEBUG

# debug toolbar's settings -- see  http://github.com/robhudson/django-debug-toolbar
INTERNAL_IPS = ('127.0.0.1', '10.154.4.75', '10.154.7.179', '192.168.1.105')
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': None,
    'EXTRA_SIGNALS': [],
    'HIDE_DJANGO_SQL': True,
    'TAG': 'div',
}

# apps
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.messages',
    'debug_toolbar',
    'django_extensions',
    'entelib.baseapp',
)

AUTHENTICATION_BACKENDS = (
    'entelib.auth_backends.CustomUserModelBackend',
)

FORCE_SCRIPT_NAME = ''
AUTH_PROFILE_MODULE = 'baseapp.UserProfile'
