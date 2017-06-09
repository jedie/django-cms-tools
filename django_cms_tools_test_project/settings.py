# coding: utf-8

"""
    Django settings for test_project project.

    Good startpoint fot Django-CMS stuff is:

    https://github.com/nephila/djangocms-installer/blob/develop/djangocms_installer/config/settings.py


    For more information on this file, see
    https://docs.djangoproject.com/en/1.8/topics/settings/

    For the full list of settings and their values, see
    https://docs.djangoproject.com/en/1.8/ref/settings/
"""

from __future__ import absolute_import, print_function, unicode_literals

print("Use settings:", __file__)


import os

from django.utils.translation import ugettext_lazy as _


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'Only for the tests ;)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SITE_ID=1


ALLOWED_HOSTS = ['*']

from django_tools.settings_utils import InternalIps
INTERNAL_IPS = InternalIps(["127.0.0.1", "::1", "192.168.*.*", "10.0.*.*"])


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'cms', # https://github.com/divio/django-cms
    'menus', # Part of Django-CMS

    'treebeard', # https://github.com/django-treebeard/django-treebeard
    'sekizai', # https://github.com/ojii/django-sekizai
    'djangocms_text_ckeditor', # https://github.com/divio/djangocms-text-ckeditor

    # Own management commands:
    'django_cms_tools.filer_tools',

    # Test project stuff:
    'django_cms_tools_test_project.test_app',
    'django_cms_tools_test_project.test_cms_plugin',
)

MIDDLEWARE_CLASSES = (
    'cms.middleware.utils.ApphookReloadMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
)

ROOT_URLCONF = 'django_cms_tools_test_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            "django_cms_tools_test_project/templates/",
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.template.context_processors.csrf',
                'django.template.context_processors.tz',
                'sekizai.context_processors.sekizai',
                'django.template.context_processors.static',
                'cms.context_processors.cms_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'test_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        # 'NAME': ":memory:"
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en'

# https://docs.djangoproject.com/en/1.8/ref/settings/#languages
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGES = (
  ('de', _('German')),
  ('en', _('English')),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


PASSWORD_HASHERS = ( # Speedup tests
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

# Basic Django CMS settings

CMS_TEMPLATES = (
    ('base.html', 'Basic Page'),
)
CMS_PERMISSION = True

# Basic Placeholder config

# from djangocms_text_ckeditor.cms_plugins import TextPlugin
CKEDITOR = "TextPlugin"

class PlaceholderContent(object):
    name = "content"

    @classmethod
    def config(cls, text="foobar"):
        return {
            'name': _("Content"),
            'plugins': [CKEDITOR],
            'default_plugins': [
                {
                    'plugin_type': CKEDITOR,
                    'values': {'body': text},
                },
            ],
        }

CMS_PLACEHOLDER_CONF = {
    PlaceholderContent.name: PlaceholderContent.config(text="Lorem ipsum dolor sit amet"),
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(msecs)d %(module)s.%(funcName)s line %(lineno)d: %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {'class': 'logging.NullHandler',},
        'console': {
            'class': 'logging.StreamHandler',
            # 'formatter': 'simple'
            'formatter': 'verbose'
        },
    },
    'loggers': {
        "django_cms_tools": {
            'handlers': [
                # 'null',
                'console'
            ],
            'level': 'DEBUG',
        },
    },
}
