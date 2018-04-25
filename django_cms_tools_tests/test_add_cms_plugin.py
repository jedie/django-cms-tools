# Django CMS Tools
from django_cms_tools.unittest_utils.add_cms_plugin import TestAddPluginTestCase


class AddPluginTestCase(TestAddPluginTestCase):
    """
    Tests for djangocms_text_ckeditor.Text

    Based on a skeleton generated via:
        ./manage.py generate_add_plugin_test_code djan
    """

    def test_textplugin_de(self):
        # plugin name in de: 'Text'
        self.create_plugin(
            language_code = "de",
            plugin_parent=None,
            plugin_type="TextPlugin",

            post_data={
                "body": ( # TextField, Text
                    '<h3>dummy text in de</h3>\n'
                    '<p>Lorem ipsum dolor sit amet, consectetur adipisici elit...</p>'
                ),
            }
        )
        response = self.assert_plugin(
            language_code="de",
            must_contain=[
                "<h3>dummy text in de</h3>",
                "<p>Lorem ipsum dolor sit amet, consectetur adipisici elit...</p>",
            ],
            template_name="cms/plugins/text.html",
        )

    def test_textplugin_en(self):
        self.create_plugin(
            language_code = "en",
            plugin_parent=None,
            plugin_type="TextPlugin",

            post_data={
                "body": ( # TextField, Text
                    '<h3>dummy text in en</h3>\n'
                    '<p>Lorem ipsum dolor sit amet, consectetur adipisici elit...</p>'
                ),
            }
        )
        response = self.assert_plugin(
            language_code="en",
            must_contain_html=[
                "<h3>dummy text in en</h3>",
                "<p>Lorem ipsum dolor sit amet, consectetur adipisici elit...</p>",
            ],
        )

