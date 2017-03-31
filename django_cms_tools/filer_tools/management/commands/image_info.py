# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

import logging

from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.template.defaultfilters import filesizeformat

from django_cms_tools.filer_tools.helper import collect_all_filer_ids, \
    iter_filer_fields, filer_obj_exists

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Display information about filer files'

    def handle(self, *args, **options):
        self.verbosity = int(options.get('verbosity'))

        total_existing_images = 0
        total_missing_images = 0
        for app_name, model, object_name, fields in iter_filer_fields():
            queryset = model.objects.all()
            model_count = queryset.count()
            self.stdout.write("\n%i items - %s.%s" % (model_count, app_name, model.__name__))

            instance_checked = 0
            existing_images = dict([(field, 0) for field in fields])
            ignore_blank = existing_images.copy()
            missing_images = existing_images.copy()

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
                        total_missing_images += 1
                        missing_images[field] += 1

                instance_checked += 1

            self.stdout.write("%i instanced checked:" % instance_checked)

            for field in fields:
                prefix = "%4i exist %4i missing %4i ignored" % (
                    existing_images[field], missing_images[field], ignore_blank[field]
                )
                self.stdout.write("%s - %s.%s.%s" % (
                    prefix, app_name, model.__name__, field.name,
                ))

        self.stdout.write("total:")
        self.stdout.write("\texisting images..: %i" % total_existing_images)
        self.stdout.write("\tmissing images...: %i" % total_missing_images)
        self.stdout.write("-"*79)

        self.stdout.write("Collect all filer IDs...")

        filer_ids = collect_all_filer_ids(
            verbose=self.verbosity>1
        )

        for model_class, ids in filer_ids.items():
            print("%s: %i entries" % (model_class.__name__, len(ids)))

        for model_class, ids in filer_ids.items():
            print("Information about %s:" % model_class.__name__)

            queryset = model_class.objects.all()
            print("\tTotal entry count: %i entries." % queryset.count())
            print("\tUsed entry count: %i entries." % len(ids))

            class_total_size = queryset.aggregate(Sum('_file_size'))
            class_total_size = class_total_size["_file_size__sum"]
            print("\tTotal size: %s" % filesizeformat(class_total_size))

            class_used_size = queryset.filter(pk__in=ids).aggregate(Sum('_file_size'))
            class_used_size = class_used_size["_file_size__sum"]
            print("\tUsed size: %s" % filesizeformat(class_used_size))

        print("(Note: 'File' contains 'Image' ;)")
