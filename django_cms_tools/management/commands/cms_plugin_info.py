# coding: utf-8

"""
    $ ./manage.py cms_plugin_info

    created 2018 by Jens Diemer
"""

from collections import defaultdict

from django.core.management.base import BaseCommand

from cms.plugin_pool import plugin_pool


class Command(BaseCommand):
    help = "List all registered plugins"

    def handle(self, *args, **options):
        self.stdout.write("There are %i CMS plugins:" % len(plugin_pool.plugins))

        plugin_info = defaultdict(list)

        for plugin_name, plugin in plugin_pool.plugins.items():
            plugin_info[plugin.module].append(
                (plugin_name, plugin)
            )

        for module, plugins in sorted(plugin_info.items()):
            self.stdout.write(self.style.NOTICE(repr(module)))
            for plugin_name, plugin in plugins:
                self.stdout.write(
                    "    * %s (%s)" % (plugin_name, plugin.name)
                )
