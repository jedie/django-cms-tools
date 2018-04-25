
"""
    :created: 24.04.2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import sys

from django.conf import settings
from django.db import models
from django.utils import translation

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.model_test_code_generator import ModelTestGenerator


class CmsPluginUnittestGenerator:
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

            for no, entry in enumerate(language_qs, 1):
                prefix_lines = [
                    "",
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
                references = []
                post_data = []
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

                    comment = field.description % {
                        "max_length": field.max_length,
                    }
                    post_data.append(
                        "{name!r}: {value!r}, # {internal_type}, {comment}".format(
                            name = field.name,
                            value = value,
                            internal_type = internal_type,
                            comment = comment

                        )
                    )
                    if internal_type == "CharField" and value:
                        references.append(value)

                item_lines.append('    post_data={')
                item_lines += ["        %s" % line for line in post_data]
                item_lines += [
                    '    }',
                    ')',
                    'response = self.assert_plugin(',
                    '    language_code="%s",' % language_code,
                    '    must_contain_html=[',
                    '        "<XXX></XXX>", # TODO: Add plugin html output here!',
                    '    ],',
                    '    must_contain=[',
                ]

                added_references = 0
                for value in references:
                    if value.strip():
                        added_references += 1
                        item_lines.append('        "%s",' % value)

                if not added_references:
                    item_lines.append('        "XXX", # TODO: Add plugin output here!')

                item_lines += [
                    '    ],',
                    '    template_name="%s",' % plugin.render_template,
                    ')',
                ]

                item_lines = ["    %s" % line for line in item_lines]

                item_lines = prefix_lines + item_lines
                lines += item_lines

        lines = ["    %s" % line for line in lines] # indent all lines

        # Add 'header':
        prefix_lines = [
            "from django_cms_tools.unittest_utils.add_cms_plugin import TestAddPluginTestCase",
            "",
            "class AddPluginTestCase(TestAddPluginTestCase):",
            '    """',
            '    Tests for %s' % model_label,
            '',
            '    Based on a skeleton generated via:',
            '        %s' % " ".join(sys.argv),
            '    """',
        ]
        lines = prefix_lines + lines

        content = "\n".join(lines)
        return content
