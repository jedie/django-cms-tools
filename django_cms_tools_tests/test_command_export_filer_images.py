"""
    :created: 24.04.2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import shutil
import tempfile

from django.core.management import CommandError, call_command

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.django_command import DjangoCommandMixin
from django_tools.unittest_utils.mockup import ImageDummy
from django_tools.unittest_utils.stdout_redirect import StdoutStderrBuffer
from django_tools.unittest_utils.unittest_base import BaseUnittestCase
from django_tools.unittest_utils.user import TestUserMixin

# Django CMS Tools
from django_cms_tools_test_project.test_cms_plugin.models import ImageModel


class ExportFilerImagesTestCase1(DjangoCommandMixin, BaseUnittestCase):

    def test_no_destination(self):
        with self.assertRaises(CommandError) as context_manager:
            call_command("export_filer_images")

        self.assertEqual(context_manager.exception.args, ('Error: the following arguments are required: destination',))

    def test_destination_not_exists(self):
        with StdoutStderrBuffer() as buff:
            with self.assertRaises(SystemExit):
                call_command("export_filer_images", "does/not/exists")

        output = buff.get_output()
        print(output)

        self.assertIn("does/not/exists' is not a existing directory", output)


class ExportFilerImagesTestCase2(TestUserMixin, DjangoCommandMixin, BaseUnittestCase):

    def setUp(self):
        super().setUp()
        self.temp_path = tempfile.mkdtemp(prefix="djangocmstools_%s_" % self._testMethodName)

    def tearDown(self):
        super().tearDown()
        try:
            shutil.rmtree(self.temp_path)
        except (OSError, IOError):
            pass

    def test_no_images(self):
        with StdoutStderrBuffer() as buff:
            with self.assertRaises(SystemExit):
                call_command("export_filer_images", self.temp_path)

        output = buff.get_output()
        print(output)

        self.assertIn("There are 0 images in database.", output)
        self.assertIn("ERROR: There are not images in database!", output)

    def test_export(self):

        user = self.login(usertype='superuser')
        instance = ImageModel()
        dummy = ImageDummy(width=100, height=50).create_temp_filer_info_image(text="foobar", user=user)
        instance.image = dummy
        instance.save()

        with StdoutStderrBuffer() as buff:
            call_command("export_filer_images", self.temp_path)

        output = buff.get_output()
        print(output)

        self.assertIn("1 items - django_cms_tools_test_project.test_cms_plugin.ImageModel", output)
        self.assertIn("All filer files saved:", output)
        self.assertIn("1 filer files saved", output)

        # TODO: Check if file really save with the right content
