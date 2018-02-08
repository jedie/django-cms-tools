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
            call_command("cms_plugin_info")
        output = buff.get_output()
        print(output)

        self.assertEqual_dedent(output,
            """
            There are 6 CMS plugins:
            Django CMS Tools Test
                * RelatedPlugin (Related Plugin)
            Generic
                * AliasPlugin (Alias)
                * AnchorPlugin (Anchor)
                * DropDownAnchorMenuPlugin (Drop-Down Anchor Menu)
                * PlaceholderPlugin (Placeholder)
                * TextPlugin (Text)
            """
        )
