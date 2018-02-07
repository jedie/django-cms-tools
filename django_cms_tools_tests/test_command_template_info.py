# coding: utf-8

from __future__ import print_function, unicode_literals

import os

from django.core.management import call_command

from cms.models import Page

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.django_command import DjangoCommandMixin
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer
from django_tools.unittest_utils.unittest_base import BaseUnittestCase

# Django CMS Tools
import django_cms_tools_test_project
from django_cms_tools.fixtures.pages import create_cms_index_pages
from django_cms_tools_test_project.test_cms_plugin.fixtures import create_testapp_cms_plugin_page

MANAGE_DIR = os.path.abspath(os.path.dirname(django_cms_tools_test_project.__file__))


class TestTemplateInfoCommand(DjangoCommandMixin, BaseUnittestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        assert Page.objects.all().count() == 0
        create_cms_index_pages()
        assert Page.objects.all().count() == 2
        create_testapp_cms_plugin_page()
        assert Page.objects.all().count() == 4

    def test_image_info(self):
        with StdoutStderrBuffer() as buff:
            call_command("template_info")
        output = buff.get_output()
        print(output)

        self.assertNotIn("ERROR", output)
        self.assertIn("There are 2 public pages:", output)
        self.assertIn("INHERIT", output)

    # TODO: Add real tests ;)
