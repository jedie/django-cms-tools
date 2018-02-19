from cms.models import Page

from django_cms_tools.plugin_anchor_menu.fixtures import create_anchor_test_page
from django_tools.unittest_utils.unittest_base import BaseTestCase


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
