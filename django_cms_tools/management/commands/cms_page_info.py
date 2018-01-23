# coding: utf-8

"""
    created 2017 by Jens Diemer
"""
import sys

import django
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Field
from django.utils import translation

from cms.models import Page


class Command(BaseCommand):
    help = "List all CMS pages and display page attributes"

    def add_arguments(self, parser):
        parser.add_argument(
            "--drafts", "-d", action="store_true",
            help="List all Page attributes"
        )
        parser.add_argument(
            "--list", "-l", action="store_true",
            help="List all Page attributes"
        )
        parser.add_argument(
            "attributes", nargs="*",
            help="List these page attributes. (e.g.: 'template', 'soft_root' etc.)"
        )

    def list_page_attributes(self):
        for field in Page._meta.get_fields(include_parents=True, include_hidden=False):
            print(field.name)

    def handle(self, *args, **options):

        if options.get("list"):
            return self.list_page_attributes()

        drafts = options.get("drafts")
        # print("drafts: %r" % drafts)

        attributes = options.get("attributes")
        # print("attributes: %r" % attributes)

        if not attributes:
            self.stdout.write("ERROR: No attributes given! Please call: --help ;)")
            sys.exit(-1)

        if drafts:
            self.stdout.write("Display attributes from 'drafts':\n")
            pages = Page.objects.drafts()
        else:
            self.stdout.write("Display attributes from 'public' pages:\n")
            pages = Page.objects.public()

        if pages.count() == 0:
            self.stdout.write("Error there are no pages ;)")
            return

        for page in pages:
            try:
                url = page.get_absolute_url()
            except Exception as err:
                url = "<ERROR: %s>" % err

            self.stdout.write(
                "pk:{pk} {url:45}".format(pk=page.pk, url=url),
                ending=" "
            )
            for attribute in attributes:
                # FIXME: Better output format!
                self.stdout.write("%30s:" % attribute, ending=" ")
                value = getattr(page, attribute, "-")
                self.stdout.write(repr(value), ending=" ")

            self.stdout.write("\n", ending=" ")
