
"""
    :created: 24.04.2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.conf import settings
from django.db import models
from django.utils import translation

from cms.models import CMSPlugin
from cms.plugin_pool import plugin_pool

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.model_test_code_generator import ModelTestGenerator


class CmsPluginUnittestGenerator:
    def iter_plugins(self):
        plugin_types = CMSPlugin.objects.all().order_by('plugin_type')

        try:
            plugin_types = set(plugin_types.distinct('plugin_type').values_list("plugin_type", flat=True))
        except NotImplementedError:
            # e.g.: sqlite has no distinct
            plugin_types = set(plugin_types.values_list("plugin_type", flat=True))

        data = []
        for plugin_type in plugin_types:
            plugin = plugin_pool.get_plugin(name=plugin_type)
            model = plugin.model
            app_label = model._meta.app_label

            label = "%s.%s" % (app_label, plugin_type)
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

    def generate(self, plugin_type, plugin, count):
        plugin_model = plugin.model
        model_label = plugin_model._meta.label
        model_test_generator = ModelTestGenerator()

        queryset = plugin_model.objects.all()

        lines = []
        for language_code, lang_name in settings.LANGUAGES:
            language_qs = queryset.filter(language=language_code)
            language_qs = language_qs[:count]

            existing_count = language_qs.count()
            if existing_count==0:
                print("#")
                print("# %r doesn't exists in '%s'" % (model_label, language_code))
                print("#")
                continue

            if existing_count<count:
                print("#")
                print("# Warning: They exists only %i items in %r!" % (existing_count, model_label))
                print("#")

            references = []
            for no, entry in enumerate(language_qs, 1):
                prefix_lines = [
                    "",
                    "#"*79,
                    "#",
                    "def test_{type}_{lang}_{no}(self):".format(
                        type = plugin_type.lower(),
                        lang= language_code,
                        no = no,
                    ),
                ]
                if language_code != "en":
                    with translation.override(language_code):
                        prefix_lines.append(
                            "    # plugin name in %s: '%s'" % (language_code, plugin.name)
                        )

                item_lines = [
                    "self.create_plugin(",
                    '    language_code = "%s",' % language_code,
                    '    plugin_parent=None,',
                    '    plugin_type="%s",' % plugin_type,
                    "",
                ]
                for field in plugin.model._meta.fields: # django.db.models.fields.Field
                    if field.hidden:
                        continue

                    if not field.editable:
                        continue

                    internal_type = field.get_internal_type()
                    if internal_type == "AutoField":
                        continue

                    if field.name == "cmsplugin_ptr":
                        continue

                    value = getattr(entry, field.name)
                    if isinstance(value, models.Model):
                        prefix_lines += [
                            "    %s" % line
                            for line in model_test_generator.test_code_for_instance(instance=value)
                        ]
                        continue

                    item_lines.append(
                        "    {name}={value!r}, # {internal_type}, {comment}".format(
                            name = field.name,
                            value = value,
                            internal_type = internal_type,
                            comment = field.description

                        )
                    )
                    if internal_type == "CharField" and value:
                        references.append(value)

                item_lines.append(')')

                item_lines.append('response = self.assert_plugin("en",')
                added_references = 0
                for value in references:
                    if value.strip():
                        added_references += 1
                        item_lines.append('    "%s",' % value)

                if not added_references:
                    item_lines.append('    "XXX", # TODO: Add plugin output here!')
                item_lines.append(')')

                item_lines.append('self.assertTemplateUsed(response, template_name="%s")' % plugin.render_template)
                item_lines.append('self.assertResponse(response,')
                item_lines.append('    must_contain=(')
                item_lines.append("        '<XXX></XXX>', # TODO: Add plugin html output here!")
                item_lines.append('    ),')
                item_lines.append('    html=True,')
                item_lines.append(')')

                item_lines = ["    %s" % line for line in item_lines]

                item_lines = prefix_lines + item_lines
                lines += item_lines

        content = "\n".join(lines)
        return content

    # def from_queryset(self, queryset):

