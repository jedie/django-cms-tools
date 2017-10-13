# coding: utf-8

"""
    created 2017 by Jens Diemer
"""

from cms.models import Page
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import translation


class Command(BaseCommand):
    help = 'Display information about CMS page templates'

    def handle(self, *args, **options):
        pages = Page.objects.public()

        self.stdout.write("There are %i public pages:\n" % pages.count())

        for page in pages:
            self.stdout.write(
                "pk:{pk} {url:45} {template}\n".format(
                    pk=page.pk,
                    url=page.get_absolute_url(),
                    template=page.template
                )
            )
