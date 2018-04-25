
"""
    :created: 24.04.2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from cms.models import CMSPlugin
from cms.plugin_pool import plugin_pool


class CmsPluginList:
    def get_plugin_by_type(self, plugin_type):
        plugin = plugin_pool.get_plugin(name=plugin_type)
        model = plugin.model
        app_label = model._meta.app_label

        label = "%s.%s" % (app_label, plugin_type)
        return (label, plugin_type, plugin)

    def iter_plugins(self):
        plugin_types = CMSPlugin.objects.all().order_by('plugin_type')

        try:
            plugin_types = set(plugin_types.distinct('plugin_type').values_list("plugin_type", flat=True))
        except NotImplementedError:
            # e.g.: sqlite has no distinct
            plugin_types = set(plugin_types.values_list("plugin_type", flat=True))

        data = []
        for plugin_type in plugin_types:
            label, plugin_type, plugin = self.get_plugin_by_type(plugin_type)
            data.append(
                (label, plugin_type, plugin)
            )

        yield from sorted(data)

    def print_all_plugins(self):
        print("All CMS plugin types:")
        plugin_count = 0
        for label, plugin_type, plugin in self.iter_plugins():
            model = plugin.model
            count = model.objects.all().count()
            print("%6i instances: %r" % (count, label))
            plugin_count += 1
        print("\nThere are %i plugins.\n" % plugin_count)

    def get_plugins_startwith_label(self, prefix):
        plugins = []
        for label, plugin_type, plugin in self.iter_plugins():
            if label.startswith(prefix):
                plugins.append(
                    (plugin_type, plugin)
                )

        return plugins
