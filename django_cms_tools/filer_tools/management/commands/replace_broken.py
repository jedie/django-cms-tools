# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

import logging
import sys

from django.core.management.base import BaseCommand

from filer.models.imagemodels import Image

from django_cms_tools.filer_tools.helper import filer_obj_exists, \
    iter_filer_fields

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Replace broken filer files'

    def add_arguments(self, parser):
        parser.add_argument('id', type=int, metavar='id',
            help=(
                "File image ID for the fallback image,"
                " used to replace not existing images"
            )
        )

    def handle(self, *args, **options):
        self.verbosity = int(options.get('verbosity'))

        image_fallback_id=int(options.get("id"))

        try:
            fallback_image = Image.objects.get(pk=image_fallback_id)
        except Image.DoesNotExist as err:
            self.stderr.write("Error: Given filer instance ID %r doesn't exist!" % image_fallback_id)
            self.stderr.write("(Origin error: %s)" % err)
            sys.exit(1)

        if not filer_obj_exists(fallback_image, verbose=True):
            self.stderr.write("Given filer image ID %r doesn't exists!" % image_fallback_id)
            sys.exit(1)

        self.stdout.write("Use fallback image: %s" % fallback_image)

        total_existing_images = 0
        total_replace_images = 0
        for app_name, model, object_name, fields in iter_filer_fields():
            queryset = model.objects.all()
            model_count = queryset.count()
            self.stdout.write("\n%i items - %s.%s" % (model_count, app_name, model.__name__))

            instance_checked = 0
            existing_images = dict([(field, 0) for field in fields])
            ignore_blank = existing_images.copy()
            replace_images = existing_images.copy()

            for instance in queryset:
                for field in fields:
                    file_obj = getattr(instance, field.name)
                    if file_obj is None:
                        ignore_blank[field] += 1
                        continue

                    exists = filer_obj_exists(file_obj, verbose=self.verbosity>2)
                    if exists:
                        total_existing_images += 1
                        existing_images[field] += 1
                    else:
                        setattr(instance, field.name, fallback_image)
                        instance.save()
                        total_replace_images += 1
                        replace_images[field] += 1

                instance_checked += 1

            self.stdout.write("%i instanced checked:" % instance_checked)

            for field in fields:
                prefix = "%4i exist %4i replaced %4i ignored" % (
                    existing_images[field], replace_images[field], ignore_blank[field]
                )
                self.stdout.write("%s - %s.%s.%s" % (
                    prefix, app_name, model.__name__, field.name,
                ))

        self.stdout.write("total:")
        self.stdout.write("\texisting images..: %i" % total_existing_images)
        self.stdout.write("\treplaced images..: %i" % total_replace_images)
