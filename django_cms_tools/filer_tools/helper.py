# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

import collections
import logging

from django.apps import apps
from django.conf import settings

from easy_thumbnails.exceptions import InvalidImageFormatError
from filer.fields.file import FilerFileField
from filer.utils.loader import load_model

log = logging.getLogger(__name__)


def iter_filer_fields():
    app_configs = apps.get_app_configs()
    for app_config in app_configs:
        app_name= app_config.name

        models = app_config.get_models()
        for model in models:
            object_name = model._meta.object_name

            fields = [field for field in model._meta.fields if isinstance(field, FilerFileField)]
            if fields:
                yield (app_name, model, object_name, fields)


def iter_filer_file_objects(exclude_empty=True, verbose=False):
    for app_name, model, object_name, fields in iter_filer_fields():
        if verbose:
            print(app_name, model, object_name, fields)

        queryset = model.objects.all()

        if exclude_empty:
            # Filter "empty" entries:
            for field in fields:
                kwargs = {"%s__exact" % field.name: None}
                queryset = queryset.exclude(**kwargs)

        for instance in queryset:
            for field in fields:
                file_obj = getattr(instance, field.name)
                yield (instance, field, file_obj)


def collect_all_filer_ids(verbose=False):
    filer_ids = collections.defaultdict(set)

    for app_name, model, object_name, fields in iter_filer_fields():
        model_pgk_name = "%s.%s" % (app_name, object_name)
        if verbose:
            print(model_pgk_name)

        for field in fields:
            ids = model.objects.values_list(field.name, flat=True)
            ids = set(ids)
            filer_ids[field.default_model_class].update(ids)

    if verbose:
        for model_class, ids in filer_ids.items():
            print("%s: %i entries" % (model_class, len(ids)))

    return filer_ids


def get_filer_attr(file_obj, attr_name):
    Image = load_model(settings.FILER_IMAGE_MODEL)
    if not isinstance(file_obj, Image):
        raise AttributeError("'%s' is not a '%s' instance!" % (repr(file_obj), repr(Image)))

    try:
        return getattr(file_obj, attr_name)
    except InvalidImageFormatError as err:
        raise AttributeError("Can't get '%s' from '%s': %s" % (attr_name, repr(file_obj), err))


def filer_obj_exists(file_obj, verbose=False):
    if file_obj is None:
        msg = "No file obj given"
        if verbose:
            print(msg)
        else:
            log.error(msg)
        return False

    Image = load_model(settings.FILER_IMAGE_MODEL)
    if isinstance(file_obj, Image):
        try:
            icons = get_filer_attr(file_obj, attr_name="icons")
        except AttributeError as err:
            if verbose:
                print(err)
            else:
                log.error(err)
        else:
            if icons:
                return True

            msg = "'%s' hasn't .icons" % repr(file_obj)
            if verbose:
                print(msg)
            else:
                log.error(msg)

        try:
            thumbnails = get_filer_attr(file_obj, attr_name="thumbnails")
        except AttributeError as err:
            if verbose:
                print(err)
            else:
                log.error(err)
        else:
            if thumbnails:
                return True

            msg = "'%s' hasn't .thumbnails" % repr(file_obj)
            if verbose:
                print(msg)
            else:
                log.error(msg)


    file = file_obj.file
    try:
        head = file.read(10)
    except Exception as err:
        # Catch 'Exception' here, because of differend errors, depends on
        # used file storage backend.
        # e.g.: IOError, AzureMissingResourceHttpError etc.
        msg="Read file error: %s" % err
        if verbose:
            print(msg)
        else:
            log.error(msg)

        return False
    finally:
        file.close()

    # print("head:", repr(head))
    if len(head):
        return True

    msg="file '%s' is empty" % repr(file_obj)
    if verbose:
        print(msg)
    else:
        log.error(msg)
    return False
