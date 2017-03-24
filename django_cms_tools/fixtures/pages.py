# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

import logging

import pytest

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
        for code, lang_name in settings.LANGUAGES:
            title = 'index in %s' % lang_name
            print('\tcreate %r' % title)
            if code != settings.LANGUAGE_CODE:
                create_title(code, title, index_page)
            add_plugin(
                placeholder=placeholder,
                plugin_type='TextPlugin', # djangocms_text_ckeditor
                language=code,
                body='index page in %s' % lang_name
            )
            index_page.publish(code)
    else:
        log.debug('Index page already exists.')

