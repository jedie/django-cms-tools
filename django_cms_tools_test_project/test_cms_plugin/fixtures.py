# coding: utf-8

"""
    created 2017 by Jens Diemer
"""

from __future__ import absolute_import, print_function, unicode_literals

import logging

from cms.api import add_plugin

from django_cms_tools_test_project.test_cms_plugin.models import EntryModel

# Django CMS Tools
from django_cms_tools.fixtures.languages import iter_languages
from django_cms_tools.fixtures.pages import CmsPageCreator, CmsPluginPageCreator
from django_cms_tools_test_project.test_cms_plugin.cms_plugin import RelatedPlugin

log = logging.getLogger(__name__)


def create_testapp_cms_plugin_page():
    """
    Create cms plugin page for the test app in all existing languages
    """
    CmsPluginPageCreator(
        apphook='SimpleTestApp',
        apphook_namespace='simpletest',
    ).create()


class RelatedPluginPageCreator(CmsPageCreator):
    def get_title(self, language_code, lang_name):
        return "Related CMS Plugin Test"

    def add_plugins(self, page, placeholder):
        for language_code, lang_name in iter_languages(self.languages):
            plugin_instance = add_plugin(
                placeholder=placeholder,
                language=language_code,
                plugin_type=RelatedPlugin,
            )
            for no in range(1,8):
                EntryModel.objects.create(
                    plugin=plugin_instance,
                    text = "CMS plugin entry no.: %i" % no,
                )

            log.info('Plugin "%s" (pk:%i) added.', str(plugin_instance), plugin_instance.pk)
            placeholder.save()


class ParentCmsPageCreator(CmsPageCreator):
    placeholder_slots = () # create a empty page, without dummy content

    def __init__(self, parent_page, *args, **kwargs):
        assert parent_page.publisher_is_draft==True, "Parent page '%s' must be a draft!" % parent_page
        self.parent_page = parent_page
        super(ParentCmsPageCreator, self).__init__(*args, **kwargs)

    def get_parent_page(self):
        return self.parent_page

    def get_title(self, language_code, lang_name):
        return "parent_test"


def create_related_plugin():
    RelatedPluginPageCreator(
        placeholder_slots=("content",)
    ).create()
