# coding: utf-8

from __future__ import print_function, unicode_literals

import os
from unittest import TestCase

import pytest

from django.core.management import call_command

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.django_command import DjangoCommandMixin
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer

# Django CMS Tools
import django_cms_tools_test_project
from django_cms_tools.fixtures.pages import create_cms_index_pages
from django_cms_tools_test_project.test_cms_plugin.fixtures import create_testapp_cms_plugin_page

MANAGE_DIR = os.path.abspath(os.path.dirname(django_cms_tools_test_project.__file__))


@pytest.mark.django_db
@pytest.mark.usefixtures(
    create_cms_index_pages.__name__,
    create_testapp_cms_plugin_page.__name__,
)
class TestTemplateInfoCommand(DjangoCommandMixin, TestCase):
    def test_image_info(self):
        with StdoutStderrBuffer() as buff:
            call_command("template_info")
        output = buff.get_output()
        print(output)

        self.assertNotIn("ERROR", output)
        self.assertIn("There are 2 public pages:", output)
        self.assertIn("INHERIT", output)

    # TODO: Add real tests ;)
