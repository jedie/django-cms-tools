from cms.models import Page

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.unittest_base import BaseTestCase

# Django CMS Tools
from django_cms_tools.plugin_anchor_menu.fixtures import create_anchor_test_page
from django_cms_tools.unittest_utils.add_cms_plugin import TestAddPluginTestCase


class AnchorMenuTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        assert Page.objects.all().count() == 0
        create_anchor_test_page()
        assert Page.objects.all().count() == 2

        cls.page = Page.objects.get(is_home=True, publisher_is_draft=False)
        cls.url = cls.page.get_absolute_url(language="en")

    def test_setup(self):
        self.assertEqual(self.url, "/en/")

    def test_page_en(self):
        response = self.client.get(self.url, HTTP_ACCEPT_LANGUAGE='en')
        self.assertResponse(response,
            must_contain=(
                '<title>AnchorTestPageCreator in en</title>',

                '<select id="anchor_menu">',
                '<option>Please select</option>',
                '<option value="#dummy-text-no-0">dummy text no. 0</option>',
                '<option value="#dummy-text-no-1">dummy text no. 1</option>',

                '<span id="dummy-text-no-0"></span>',
                '<span id="dummy-text-no-1"></span>',

                'var select_menu=$("#anchor_menu");'
            ),
            html=False,
            must_not_contain=('error', 'traceback'),
            messages=[],
            template_name='base.html',
        )

    # TODO: test AnchorPluginModel.validate_unique
    # TODO: test DropDownAnchorMenuPlugin functionality
    # TODO: test JS functionality, too ;)



class AddPluginTestCase(TestAddPluginTestCase):
    """
    Tests for plugin_anchor_menu.AnchorPluginModel

    Based on a skeleton generated via:
        ./manage.py generate_add_plugin_test_code plugin_anchor_menu.AnchorPlugin
    """
    def test_anchorplugin_de_1(self):
        # plugin name in de: 'Anchor'
        # plugin_anchor_menu.AnchorPluginModel
        self.create_plugin(
            language_code = "de",
            plugin_parent=None,
            plugin_type="AnchorPlugin",

            post_data={
                "title": 'dummy text no. 0', # CharField, String (up to 254)
                "slug": 'dummy-text-no-0', # SlugField, Slug (up to 255)
            }
        )
        response = self.assert_plugin(
            language_code="de",
            must_contain_html=[
                '<span id="dummy-text-no-0"></span>',
            ],
            must_contain=[],
            template_name="anchor_menu/anchor.html",
        )

    def test_anchorplugin_de_2(self):
        # plugin name in de: 'Anchor'
        # plugin_anchor_menu.AnchorPluginModel
        self.create_plugin(
            language_code = "de",
            plugin_parent=None,
            plugin_type="AnchorPlugin",

            post_data={
                "title": 'dummy text no. 1', # CharField, String (up to 254)
                "slug": 'dummy-text-no-1', # SlugField, Slug (up to 255)
            }
        )
        response = self.assert_plugin(
            language_code="de",
            must_contain_html=[
                '<span id="dummy-text-no-1"></span>',
            ],
            must_contain=[],
            template_name="anchor_menu/anchor.html",
        )

    def test_anchorplugin_en_1(self):
        # plugin_anchor_menu.AnchorPluginModel
        self.create_plugin(
            language_code = "en",
            plugin_parent=None,
            plugin_type="AnchorPlugin",

            post_data={
                "title": 'dummy text no. 2', # CharField, String (up to 254)
                "slug": 'dummy-text-no-2', # SlugField, Slug (up to 255)
            }
        )
        response = self.assert_plugin(
            language_code="en",
            must_contain_html=[
                '<span id="dummy-text-no-2"></span>',
            ],
            must_contain=[],
            template_name="anchor_menu/anchor.html",
        )

    def test_anchorplugin_en_2(self):
        # plugin_anchor_menu.AnchorPluginModel
        self.create_plugin(
            language_code = "en",
            plugin_parent=None,
            plugin_type="AnchorPlugin",

            post_data={
                "title": 'dummy text no. 3', # CharField, String (up to 254)
                "slug": 'dummy-text-no-3', # SlugField, Slug (up to 255)
            }
        )
        response = self.assert_plugin(
            language_code="en",
            must_contain_html=[
                '<span id="dummy-text-no-3"></span>',
            ],
            must_contain=[],
            template_name="anchor_menu/anchor.html",
        )
