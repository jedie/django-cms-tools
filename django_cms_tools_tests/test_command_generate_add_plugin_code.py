
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
            call_command("generate_add_plugin_test_code")
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

    def test_generate(self):
        with StdoutStderrBuffer() as buff:
            call_command("generate_add_plugin_test_code", "djangocms_text_ckeditor.TextPlugin")
        output = buff.get_output()
        print(output)

        self.assertIn("def test_textplugin_de_1(self):", output)
        self.assertIn('plugin_type="TextPlugin",', output)
        self.assertIn("body='<h2>Dummy no. 1 in Deutsch (placeholder content)</h2>', # TextField, Text", output)

        self.assertIn("def test_textplugin_en_2(self):", output)
