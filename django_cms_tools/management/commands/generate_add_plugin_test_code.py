"""
    :created: 24.04.2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.core.management import BaseCommand
from django.utils import translation

# Django CMS Tools
from django_cms_tools.cms_plugin_list import CmsPluginList
from django_cms_tools.unittest_utils.cms_plugin_test_code import CmsPluginUnittestGenerator


class Command(BaseCommand):
    """
    List all CMS plugins with, e.g.:
        $ ./manage.py generate_add_plugin_test_code

    Generate unittest skeleton code, e.g.:
        $ ./manage.py generate_add_plugin_test_code cmsplugin
        $ ./manage.py generate_add_plugin_test_code djangocms
    """
    help = "Generate unittest skeletons for Django CMS plugin admin add view."

    def add_arguments(self, parser):
        parser.add_argument(
            'plugin_label',
            nargs="?",
            help='Name of the Django CMS plugin. (can only be the first characters! We use "startwith"'
        )
        parser.add_argument('--translation', help='Language code that will be activated', default="en")
        parser.add_argument('--count', help='Number of data records to be generated.', type=int, default=1)

    def handle(self, *args, **options):
        plugin_label = options['plugin_label']
        language_code = options["translation"]
        count = int(options["count"])

        translation.activate(language_code)

        cms_plugin_list = CmsPluginList()

        if plugin_label is None:
            print("\nNo plugin-type given.\n")
            cms_plugin_list.print_all_plugins()
            return

        plugins = cms_plugin_list.get_plugins_startwith_label(plugin_label)
        if not plugins:
            print("\nERROR: No plugins starts with given label %r\n" % plugin_label)
            cms_plugin_list.print_all_plugins()
            return

        plugin_test_generator = CmsPluginUnittestGenerator()
        for plugin_type, plugin in plugins:
            content = plugin_test_generator.generate(plugin_type, plugin, count)
            print()
            print("#" * 79)
            print(content)
            print("#" * 79)
            print()
