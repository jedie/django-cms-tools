
from django.apps import apps
from django.core.management import BaseCommand
from django.db.models import Q
from django.utils import translation

from cms.models import CMSPlugin, Page, PlaceholderField, Title

# Django CMS Tools
from django_cms_tools.cms_plugin_list import CmsPluginList


class Command(BaseCommand):
    """
    e.g.:
    $ ./manage.py list_page_by_plugin LinkPlugin
    $ ./manage.py list_page_by_plugin PlainTextPlugin
    $ ./manage.py list_page_by_plugin TextLinkTeaserPlugin
    """
    help = "Display a list of all urls that contains a Django CMS plugin."

    def add_arguments(self, parser):
        parser.add_argument('plugin_type', nargs="?", help='Name of the Django CMS plugin.')
        parser.add_argument('--translation', help='Language code that will be activated', default="en")
        parser.add_argument('--count', help='Number of data records to be generated.', type=int, default=2)

    def handle(self, *args, **options):
        plugin_type = options['plugin_type']
        language_code = options["translation"]
        count = int(options["count"])

        translation.activate(language_code)

        cms_plugin_list = CmsPluginList()

        if plugin_type is None:
            print("\nNo plugin-type given.\n")
            cms_plugin_list.print_all_plugins()
            return

        try:
            label, plugin_type, plugin = cms_plugin_list.get_plugin_by_type(plugin_type)
        except KeyError:
            print("\nERROR: Given plugin type %r doesn't exists!\n" % plugin_type)
            if "." in plugin_type:
                plugin_type = plugin_type.rsplit(".")[-1]
                print("Hint: Maybe you mean: %r ?!?\n" % plugin_type)

            cms_plugin_list.print_all_plugins()
            return

        plugin_qs = CMSPlugin.objects.filter(plugin_type = plugin_type)
        plugin_count = plugin_qs.count()
        print("Found %i %r plugins..." % (plugin_count, plugin_type), end=" ")
        if plugin_count == 0:
            print("\nAbort: No plugin found.\n")
            cms_plugin_list.print_all_plugins()
            return

        placeholders = plugin_qs.order_by('placeholder')
        try:
            placeholders = set(placeholders.distinct('placeholder').values_list("placeholder", flat=True))
        except NotImplementedError:
            # e.g.: sqlite has no distinct
            placeholders = set(placeholders.values_list("placeholder", flat=True))

        print("%i placeholders..." % len(placeholders), end=" ")

        # List all CMS pages that has the given plugin:

        pages = Page.objects.public().filter(placeholders__in=placeholders)
        page_count = pages.count()
        print("%i pages:" % page_count)

        title_qs = Title.objects.public().filter(page__placeholders__in=placeholders)
        for page in pages:
            print(" * %s" % page)

            titles = title_qs.filter(page=page)
            for title in titles:
                page = title.page
                url = page.get_public_url(language=title.language)
                print("\t* %s" % url)

        # Collect a list of all non-CMSPlugin models with a PlaceholderField:
        placeholder_field_models = []
        app_configs = apps.get_app_configs()
        for app_config in app_configs:
            models = app_config.get_models()
            for model in models:
                if issubclass(model, CMSPlugin):
                    continue

                placeholder_fields = []
                for field in model._meta.fields:
                    if isinstance(field, PlaceholderField):
                        placeholder_fields.append(field)

                if placeholder_fields:
                    placeholder_field_models.append(
                        (model, tuple(placeholder_fields))
                    )

        # List all app instances with .get_absolute_url():

        print("\nThere are %i app models with PlaceholderFields:" % len(placeholder_field_models))
        for model, placeholder_fields in placeholder_field_models:
            print(" * %s" % model._meta.object_name, end=" ")
            print("%r" % ",".join([field.name for field in placeholder_fields]), end=" ")

            qs = model.objects.all()
            entry_count = qs.count()
            print("- %i total entries" % entry_count, end=" ")
            if entry_count == 0:
                print("Skip")
                continue

            query = Q()
            for placeholder_field in placeholder_fields:
                kwarg={"%s__in" % placeholder_field.name: placeholders}
                query |= Q(**kwarg)

            qs = qs.filter(query)
            filtered_count = qs.count()
            print("- %i filtered entries" % filtered_count)
            for entry in qs:
                try:
                    url = entry.get_absolute_url()
                except Exception as err:
                    url = "<error: %s>" % err

                print("\t* (pk:%r) %s - %s" % (entry.pk, url, entry))
