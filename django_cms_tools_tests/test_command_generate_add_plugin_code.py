"""
    :created: 24.04.2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import sys

from django.core.management import call_command

from cms.models import Page

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.django_command import DjangoCommandMixin
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer
from django_tools.unittest_utils.unittest_base import BaseUnittestCase

# Django CMS Tools
import django_cms_tools_test_project
from django_cms_tools.fixtures.pages import CmsPageCreator
from django_cms_tools_test_project.test_cms_plugin.fixtures import create_related_plugin

MANAGE_DIR = os.path.abspath(os.path.dirname(django_cms_tools_test_project.__file__))


class SysArgvMock:
    def __init__(self, argv):
        self.argv = argv

    def __enter__(self):
        self.old_argv = sys.argv
        sys.argv = self.argv

    def __exit__(self, type, value, traceback):
        sys.argv = self.old_argv


class CmsPluginUnittestGeneratorTestCase(DjangoCommandMixin, BaseUnittestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        create_related_plugin()

        page, created = CmsPageCreator().create()
        assert created

        assert Page.objects.all().count() == 4  # draft + publish

    def test_list_all_plugins(self):
        with StdoutStderrBuffer() as buff:
            call_command("generate_add_plugin_test_code")
        output = buff.get_output()
        print(output)

        self.assertEqual_dedent(
            output, """
            No plugin-type given.
            
            All CMS plugin types:
                12 instances: 'djangocms_text_ckeditor.TextPlugin'
                 4 instances: 'test_cms_plugin.RelatedPlugin'
            
            There are 2 plugins.
            """
        )

    def test_generate(self):
        with StdoutStderrBuffer() as buff:

            args = ["generate_add_plugin_test_code", "djangocms_text_ckeditor"]
            with SysArgvMock(argv=["unittest"] + args):
                call_command(*args)

        output = buff.get_output()
        print(output)

        self.assertIn("Based on a skeleton generated via:", output)
        self.assertIn("unittest generate_add_plugin_test_code djangocms_text_ckeditor", output)

        self.assertIn("def test_textplugin_de_1(self):", output)
        self.assertIn("Tests for djangocms_text_ckeditor.Text in German", output)

        self.assertIn('plugin_type="TextPlugin",', output)
        self.assertIn("post_data={", output)
        self.assertIn("'body': '<h2>Dummy no. 1 in Deutsch (placeholder content)</h2>', # TextField, Text", output)

        self.assertIn("def test_textplugin_en_1(self):", output)
        self.assertIn("Tests for djangocms_text_ckeditor.Text in English", output)
        self.assertIn("'body': '<h2>Dummy no. 1 in English (placeholder content)</h2>', # TextField, Text", output)
