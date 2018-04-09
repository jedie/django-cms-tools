# coding: utf-8

"""
    List more information about uninstalled/unsaved plugins

    $ ./manage.py orphaned_plugin_info

    created 2018 by Jens Diemer
"""

import logging


from cms.models import CMSPlugin, Page
from cms.plugin_pool import plugin_pool
from django.core.management.base import BaseCommand

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Django CMS orphaned plugin info"

    def print_plugin_info(self, plugins):
        for plugin in plugins:
            placeholder = plugin.placeholder
            print(
                "\tpk: %r - language: %r - placeholder: %r" % (
                    plugin.pk, plugin.language, placeholder
                )
            )
            print("\t\tcreation date..: {:%Y-%m-%d %H:%M:%S}".format(plugin.creation_date))
            print("\t\tchanged date...: {:%Y-%m-%d %H:%M:%S}".format(plugin.changed_date))

            if placeholder:
                pages = Page.objects.filter(placeholders=placeholder)
                print("\t\tPages:", pages)

            # for attr in dir(plugin):
            #     if attr.startswith("_"):
            #         continue
            #
            #     value = getattr(plugin, attr, None)
            #     if callable(value):
            #         continue
            #
            #     print("\t%s: %r" % (attr, value))

    def handle(self, *args, **options):
        self.stdout.write("")
        self.stdout.write("_"*79)
        self.stdout.write(self.help)
        self.stdout.write("")

        all_plugins = CMSPlugin.objects.order_by('plugin_type')
        plugin_types = list(set(all_plugins.values_list('plugin_type', flat=True)))
        plugin_types.sort()

        print("There are %i CMS plugin types..." % len(plugin_types))

        uninstalled_count = 0
        unsaved_count = 0
        plugin_count = 0
        for plugin_type in plugin_types:
            # get all plugins of this type
            plugins = CMSPlugin.objects.filter(plugin_type=plugin_type)
            plugin_count += plugins.count()

            # does this plugin have a model? report unsaved instances
            try:
                plugin_pool.get_plugin(name=plugin_type)
            except KeyError:
                # catch uninstalled plugins
                txt = "{txt}: '{plugin_type}'".format(
                    txt = self.style.NOTICE("uninstalled plugin type"),
                    plugin_type = self.style.SQL_FIELD(plugin_type)
                )
                print(txt)
                uninstalled_plugins = CMSPlugin.objects.filter(plugin_type=plugin_type)
                uninstalled_count += uninstalled_plugins.count()
                self.print_plugin_info(uninstalled_plugins)
            else:
                unsaved_instances = [p for p in plugins if not p.get_plugin_instance()[0]]
                if unsaved_instances:
                    txt = "+ '{plugin_type}' has {count} {txt}:".format(
                        plugin_type= self.style.SQL_FIELD(plugin_type),
                        count = len(unsaved_instances),
                        txt = self.style.NOTICE("unsaved instances")
                    )
                    print(txt)
                    unsaved_count += len(unsaved_instances)
                    self.print_plugin_info(unsaved_instances)

        self.stdout.write("%i CMS plugins checked" % plugin_count)
        self.stdout.write("%i uninstalled CMS plugins" % uninstalled_count)
        self.stdout.write("%i unsaved CMS plugins" % unsaved_count)
        self.stdout.write("\n --- END ---\n")
