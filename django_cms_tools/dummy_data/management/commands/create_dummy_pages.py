# coding: utf-8

from __future__ import unicode_literals, print_function

from django.core.management.base import BaseCommand

from django_cms_tools.fixtures.pages import create_dummy_pages


class Command(BaseCommand):
    help = 'Create dummy CMS pages.'

    def add_arguments(self, parser):
        parser.add_argument('--fresh', action='store_true', dest='delete_first', default=False,
            help='Delete existing entries.')

    def handle(self, *args, **options):
        delete_first = options.get('delete_first')

        self.stdout.write("%s\n" % self.help)
        create_dummy_pages(
            delete_first=delete_first,
            title_prefix="dummy page",
            levels=3,
            count=3
        )
