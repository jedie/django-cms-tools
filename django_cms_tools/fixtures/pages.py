# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

import logging

import pytest

from django.utils import translation

from cms.api import create_page, create_title, add_plugin
from cms.constants import TEMPLATE_INHERITANCE_MAGIC
from cms.models import Page, CMSPlugin, settings
from cms.utils import apphook_reload


log = logging.getLogger(__name__)


@pytest.fixture()
def create_cms_index_pages(placeholder_slot="content"):
    """
    create cms home page and fill >content< placeholder with TextPlugin
    """
    try:
        Page.objects.get(is_home=True, publisher_is_draft=False)
    except Page.DoesNotExist:
        log.debug('Create index page in "en" and...')
        index_page = create_page(
            title="index in English",
            template=TEMPLATE_INHERITANCE_MAGIC,
            language=settings.LANGUAGE_CODE,
            published=False,
            in_navigation=True
        )
        placeholder, created = index_page.placeholders.get_or_create(slot=placeholder_slot)
        for language_code, lang_name in settings.LANGUAGES:
            with translation.override(language_code):
                title = 'index in %s' % lang_name
                print('\tcreate %r' % title)
                if language_code != settings.LANGUAGE_CODE:
                    create_title(language_code, title, index_page)
                add_plugin(
                    placeholder=placeholder,
                    plugin_type='TextPlugin', # djangocms_text_ckeditor
                    language=language_code,
                    body='index page in %s' % lang_name
                )
                index_page.publish(language_code)
    else:
        log.debug('Index page already exists.')


def create_cms_plugin_page(apphook, apphook_namespace, placeholder_slot="content"):
    """
    Create cms plugin page in all existing languages.
    Add a link to the index page.

    :param apphook: e.g...........: 'FooBarApp'
    :param apphook_namespace: e.g.: 'foobar'
    :return:
    """
    try:
        index_page = Page.objects.get(is_home=True, publisher_is_draft=False)
    except Page.DoesNotExist:
        log.error('ERROR: "index page" doesn\'t exists!')
        log.error('run "./manage.py create_index_pages" first!')
        raise RuntimeError('no index page')

    plugin = CMSPlugin.objects.filter(plugin_type=apphook)
    if plugin.exists():
        log.debug('Plugin page for "%s" plugin already exist, ok.' % apphook)
    else:
        log.debug('Create "%s" plugin page in "en" and:' % apphook)

        queryset = Page.objects.filter(application_namespace=apphook_namespace)
        if queryset.exists():
            log.debug('Plugin page "%s" already exists, ok.\n' % apphook)
            return

        plugin_page = create_page(
            title='%s in English' % apphook,
            template=TEMPLATE_INHERITANCE_MAGIC,
            parent=index_page,
            language=settings.LANGUAGE_CODE,
            published=False,
            in_navigation=True,
            apphook=apphook,
            apphook_namespace=apphook_namespace
        )

        placeholder, created = index_page.placeholders.get_or_create(slot=placeholder_slot)
        for language_code, lang_name in settings.LANGUAGES:
            with translation.override(language_code):
                print('\tcreate "%s" page in: %s' % (apphook, lang_name))
                if language_code != settings.LANGUAGE_CODE:
                    create_title(language_code, '%s in %s' % (apphook, lang_name), plugin_page)

                plugin_url = plugin_page.get_absolute_url(language=language_code)
                add_plugin(
                    placeholder=placeholder,
                    plugin_type='TextPlugin', # djangocms_text_ckeditor
                    language=language_code,
                    body='<p><a href="{url}">{name}</a></p>'.format(
                        url=plugin_url,
                        name=apphook,
                    )
                )
                plugin_page.publish(language_code)

    apphook_reload.reload_urlconf()
