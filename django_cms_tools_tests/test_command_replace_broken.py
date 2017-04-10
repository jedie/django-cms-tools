# coding: utf-8

from __future__ import unicode_literals, print_function


import os
from unittest import TestCase

from django_tools.unittest_utils.django_command import DjangoCommandMixin

import django_cms_tools_test_project


MANAGE_DIR = os.path.abspath(os.path.dirname(django_cms_tools_test_project.__file__))


class TestListModelsCommand(DjangoCommandMixin, TestCase):

    def test_replace_broken_help(self):
        output = self.call_manage_py(["replace_broken", "--help"], manage_dir=MANAGE_DIR)
        print(output)

        self.assertNotIn("ERROR", output)
        self.assertIn("Replace broken filer files", output)
        self.assertIn("positional arguments:", output)
        self.assertIn("File image ID for the fallback image", output)

    # TODO: Add real tests ;)

    # def test_replace(self):
    #     file_replace_image_id = 123
    #     output = self.call_manage_py(
    #         ["replace_broken", file_replace_image_id],
    #         manage_dir=MANAGE_DIR
    #     )
    #     print(output)
    #
    #     self.assertIn("error: the following arguments are required: id", output)



