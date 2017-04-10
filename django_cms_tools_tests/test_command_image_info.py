# coding: utf-8

from __future__ import unicode_literals, print_function


import os
from unittest import TestCase

from django_tools.unittest_utils.django_command import DjangoCommandMixin

import django_cms_tools_test_project


MANAGE_DIR = os.path.abspath(os.path.dirname(django_cms_tools_test_project.__file__))


class TestListModelsCommand(DjangoCommandMixin, TestCase):

    def test_image_info_help(self):
        output = self.call_manage_py(["image_info", "--help"], manage_dir=MANAGE_DIR)
        print(output)

        self.assertNotIn("ERROR", output)
        self.assertIn("Display information about filer files", output)

    def test_image_info(self):
        output = self.call_manage_py(["image_info"], manage_dir=MANAGE_DIR)
        print(output)

        self.assertNotIn("ERROR", output)
        self.assertIn("existing images..: 0", output)
        self.assertIn("missing images...: 0", output)

    # TODO: Add real tests ;)

