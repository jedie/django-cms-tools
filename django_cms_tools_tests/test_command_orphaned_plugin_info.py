# coding: utf-8

from __future__ import print_function, unicode_literals

import os

from django.core.management import call_command

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.django_command import DjangoCommandMixin
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer
from django_tools.unittest_utils.unittest_base import BaseUnittestCase

# Django CMS Tools
import django_cms_tools_test_project

MANAGE_DIR = os.path.abspath(os.path.dirname(django_cms_tools_test_project.__file__))


class TestCmsPluginInfoCommand(DjangoCommandMixin, BaseUnittestCase):
    def test_image_info(self):
        with StdoutStderrBuffer() as buff:
            call_command("orphaned_plugin_info")
        output = buff.get_output()
        print(output)

        self.assertEqual_dedent(output,
            """
            _______________________________________________________________________________
            Django CMS orphaned plugin info
            
            There are 0 CMS plugin types...
            0 CMS plugins checked
            0 uninstalled CMS plugins
            0 unsaved CMS plugins
            
             --- END ---
            """
        )
