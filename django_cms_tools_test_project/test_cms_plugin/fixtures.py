# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function

import pytest

from django_cms_tools.fixtures.pages import CmsPluginPageCreator


@pytest.fixture()
def create_testapp_cms_plugin_page():
    """
    Create cms plugin page for the test app in all existing languages
    """
    page = CmsPluginPageCreator(
        apphook='SimpleTestApp',
        apphook_namespace='simpletest',
        placeholder_slot="content"
    ).create()
