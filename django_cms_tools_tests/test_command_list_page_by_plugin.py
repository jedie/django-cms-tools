
"""
    :created: 24.04.2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os

from django.core.management import call_command

from cms.models import Page

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.django_command import DjangoCommandMixin
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer
from django_tools.unittest_utils.unittest_base import BaseUnittestCase

# Django CMS Tools
import django_cms_tools_test_project
from django_cms_tools.fixtures.pages import CmsPageCreator

MANAGE_DIR = os.path.abspath(os.path.dirname(django_cms_tools_test_project.__file__))


class CmsPluginUnittestGeneratorTestCase(DjangoCommandMixin, BaseUnittestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        page, created = CmsPageCreator().create()
        assert created

        assert Page.objects.all().count() == 2 # draft + publish

    def test_list_all_plugins(self):
        with StdoutStderrBuffer() as buff:
            call_command("list_page_by_plugin")
        output = buff.get_output()
        print(output)

        self.assertEqual_dedent(output,
            """
            No plugin-type given.
            
            All CMS plugin types:
                12 instances: 'djangocms_text_ckeditor.TextPlugin'
            
            There are 1 plugins.
            """
        )

    def test_wrong_plugin_type(self):
        with StdoutStderrBuffer() as buff:
            call_command("list_page_by_plugin", "foobar_app.FooBarPlugin")
        output = buff.get_output()
        print(output)

        self.assertEqual_dedent(output,
            """
            ERROR: Given plugin type 'foobar_app.FooBarPlugin' doesn't exists!
            
            Hint: Maybe you mean: 'FooBarPlugin' ?!?
            
            All CMS plugin types:
                12 instances: 'djangocms_text_ckeditor.TextPlugin'
            
            There are 1 plugins.
            """
        )

    def test_TextPlugin(self):
        with StdoutStderrBuffer() as buff:
            call_command("list_page_by_plugin", "TextPlugin")
        output = buff.get_output()
        print(output)

        self.assertIn("Found 12 'TextPlugin' plugins... 2 placeholders... 1 pages:", output)
        self.assertIn("* CmsPageCreator in en", output)
        self.assertIn("* /de/", output)
        self.assertIn("* /en/", output)

        self.assertIn("There are 2 app models with PlaceholderFields:", output)
        self.assertIn("* StaticPlaceholder 'draft,public' - 0 total entries Skip", output)
        self.assertIn("* LandingPageModel 'content' - 0 total entries Skip", output)

