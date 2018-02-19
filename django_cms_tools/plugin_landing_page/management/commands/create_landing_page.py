
"""
    :create: 2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.core.management.base import BaseCommand

# Django CMS Tools
from django_cms_tools.plugin_landing_page.fixtures import LandingPageCmsPluginPageCreator


class Command(BaseCommand):
    help = "Create 'LandingPage' app page"

    def add_arguments(self, parser):
        parser.add_argument("--fresh", action="store_true", dest="delete_first", default=False,
            help="Delete existing entries.")

    def handle(self, *args, **options):
        delete_first = options.get("delete_first")

        self.stdout.write("Create 'LandingPage' app page...\n")
        LandingPageCmsPluginPageCreator(delete_first=delete_first).create()
