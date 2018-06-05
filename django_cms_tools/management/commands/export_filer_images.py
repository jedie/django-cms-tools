"""
    :created: 05.06.2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import hashlib
import logging
import sys
import time
from pathlib import Path

from django.conf import settings
from django.core import serializers
from django.core.management.base import BaseCommand
from django.template.defaultfilters import filesizeformat
from django.utils import translation

from filer.utils.loader import load_model

# Django CMS Tools
from django_cms_tools.filer_tools.helper import iter_filer_fields

log = logging.getLogger(__name__)


class ReadFileError(IOError):
    pass


def copy_file(source, destination, chunk_size):
    next_update = time.time() + 3
    bytes_written = 0
    while True:
        try:
            data = source.read(chunk_size)
        except Exception as err:
            # Catch 'Exception' here, because of differend errors, depends on
            # used file storage backend.
            # e.g.: IOError, AzureMissingResourceHttpError etc.
            raise ReadFileError(err)

        if not data:
            break

        bytes_written += len(data)
        destination.write(data)

        if time.time() > next_update:
            print("%i Bytes transfered..." % bytes_written)
            next_update = time.time() + 3

    return bytes_written


def generate_sha1_hexdigest(file_path, chunk_size):
    hash = hashlib.sha1()
    with file_path.open("rb") as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            hash.update(data)
    return hash.hexdigest()


class Command(BaseCommand):
    help = 'Export all filer files to disk.'

    def add_arguments(self, parser):
        parser.add_argument('destination', type=str, help=("Destination path to store the images."))
        parser.add_argument(
            '--chunk_size', type=int, default=8 * 1024 * 1024, help=("Chunk size for read/write the image file")
        )

    def handle(self, *args, **options):
        self.verbosity = int(options.get('verbosity'))
        chunk_size = int(options.get('chunk_size'))

        if settings.USE_I18N:
            # e.g.: Parler models needs activated translations:
            language_code = settings.LANGUAGE_CODE
            self.stdout.write("activate %r translations." % language_code)
            translation.activate(language_code)

        destination = Path(options.get("destination"))
        if not destination.is_dir():
            self.stderr.write("Given destination '%s' is not a existing directory!" % destination)
            sys.exit(-1)

        destination = Path(destination, "filer_export").resolve()
        destination.mkdir(exist_ok=True)
        self.stdout.write("Export all filer images to: '%s'..." % destination)

        self.stdout.write("settings.FILER_IMAGE_MODEL: %r" % settings.FILER_IMAGE_MODEL)

        Image = load_model(settings.FILER_IMAGE_MODEL)
        self.stdout.write("Use filer Image class: %s" % repr(Image))

        image_count = Image.objects.all().count()
        self.stdout.write("There are %i images in database." % image_count)
        if image_count == 0:
            self.stderr.write("ERROR: There are not images in database!")
            sys.exit(1)

        self.stdout.write("Calculate total sizes to transfer...")
        next_update = time.time() + 3
        total_existing_bytes = 0
        total_existing_files = 0
        for app_name, model, object_name, fields in iter_filer_fields():
            queryset = model.objects.all()
            for instance in queryset:
                for field in fields:
                    filer_field_instance = getattr(instance, field.name)
                    if filer_field_instance is not None:
                        total_existing_bytes += filer_field_instance.size
                        total_existing_files += 1
                if time.time() > next_update:
                    self.stdout.write(
                        "\t%i filer files - %s ..." % (total_existing_files, filesizeformat(total_existing_bytes))
                    )
                    next_update = time.time() + 3

        self.stdout.write("Total: %i filer files - %s" % (total_existing_files, filesizeformat(total_existing_bytes)))

        JSONSerializer = serializers.get_serializer("json")
        json_serializer = JSONSerializer()

        total_bytes_written = 0
        total_saved_files = 0
        total_existing_files = 0
        ignore_blank = 0

        try:
            for app_name, model, object_name, fields in iter_filer_fields():
                package_name = "%s.%s" % (app_name, model.__name__)
                self.stdout.write("_" * 79)
                self.stdout.write(package_name)

                path_prefix = Path(destination, package_name)

                queryset = model.objects.all()
                model_count = queryset.count()

                self.stdout.write("\n%i items - %s" % (model_count, package_name))

                for instance in queryset:
                    for field in fields:
                        field_instance = getattr(instance, field.name)
                        if field_instance is None:
                            ignore_blank += 1
                            continue

                        label = field_instance.label

                        # from filer.models import Folder
                        folder = field_instance.folder  # filer.models.foldermodels.Folder instance

                        if folder is not None:
                            pretty_logical_path = folder.pretty_logical_path
                            # self.stdout.write("pretty_logical_path:", pretty_logical_path)
                            folder_path = Path(pretty_logical_path.strip("/"))
                            # self.stdout.write("folder_path:", folder_path)
                            file_path = Path(path_prefix, folder_path, label)
                        else:
                            file_path = Path(path_prefix, label)

                        if not file_path.parent.is_dir():
                            file_path.parent.mkdir(parents=True)

                        try:
                            self.stdout.write("File: %s" % file_path.relative_to(destination))
                        except ValueError:
                            # e.g.: ValueError: '/foo/foo.png' does not start with '/bar/foo.png'
                            self.stdout.write("File: %s" % file_path)

                        # Skip image, if file with same size and same SHA1 exists:
                        if file_path.is_file():
                            self.stdout.write("File already downloaded... Check if it's the same...")
                            if file_path.stat().st_size == field_instance.size:
                                self.stdout.write("Has the same size -> check SHA1")
                                current_sha1 = generate_sha1_hexdigest(file_path, chunk_size)
                                if current_sha1 == field_instance.sha1:
                                    self.stdout.write("SHA1 is the same, skip file.")
                                    total_existing_files += 1
                                    continue

                        # Save meta data as JSON:
                        json_file_path = file_path.with_name(file_path.name + ".json")
                        with json_file_path.open("w") as f:
                            json_serializer.serialize([field_instance], stream=f)

                        # Save the Image file to disk:
                        source_file = field_instance.file
                        with file_path.open("wb") as destination_file:
                            try:
                                total_bytes_written += copy_file(source_file, destination_file, chunk_size)
                            except ReadFileError as err:
                                self.stderr.write("Error: %s" % err)
                                continue

                        total_saved_files += 1

                self.stdout.write(
                    "\n\t%i saved files - %s...\n" % (total_saved_files, filesizeformat(total_bytes_written))
                )
        except KeyboardInterrupt:
            self.stderr.write("\nAbort.")

        self.stdout.write("\nAll filer files saved:")
        self.stdout.write("\t%i filer files saved" % total_saved_files)
        self.stdout.write("\t%i existing filer files" % total_existing_files)
        self.stdout.write("\t%s written" % filesizeformat(total_bytes_written))
        self.stdout.write("Export files stored here: '%s'" % destination)
