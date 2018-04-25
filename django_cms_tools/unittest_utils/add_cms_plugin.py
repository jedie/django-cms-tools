
"""
    TestCase to test "add CMS plugin via admin"

    :create: 2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from pprint import pprint


from django.test import Client


from cms.api import publish_page
from cms.models import CMSPlugin

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.unittest_base import BaseTestCase
from django_tools.unittest_utils.user import TestUserMixin

# Django CMS Tools
from django_cms_tools.fixtures.pages import CmsPageCreator
from django_cms_tools.unittest_utils.page_mixins import CmsPageTestUtilsMixin

PLUGIN_TEST_PLACEHOLDER_SLOT="plugin_test_content"


class CmsPluginTestPageCreator(CmsPageCreator):
    template = "tests/plugin_test.html"
    in_navigation = True
    placeholder_slots = (PLUGIN_TEST_PLACEHOLDER_SLOT,)

    def get_title(self, language_code, lang_name):
        return "CMS Plugin Test Page"

    def get_slug(self, language_code, lang_name):
        return "cms_plugin_test"



class ClientBaseTestCase(CmsPageTestUtilsMixin, BaseTestCase):
    """ Main base class for all TestCases that used the Client() """
    maxDiff = None

    def setUp(self):
        super().setUp()

        # Add fresh test client
        self.client = Client()



class TestAddPluginTestCase(TestUserMixin, ClientBaseTestCase):
    """
    TestCase to test "add CMS plugin via admin"
    for generated skeleton code via:

        $ ./manage.py generate_add_plugin_test_code
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.test_page, created = CmsPluginTestPageCreator().create()
        cls.test_placeholder = cls.test_page.placeholders.all()[0]

    def setUp(self):
        super().setUp()
        plugin_qs = CMSPlugin.objects.filter(
            placeholder__slot=self.test_placeholder.slot
        )
        plugin_qs.delete()

    def create_plugin(self, language_code, plugin_parent, plugin_type, post_data):
        # placeholder_draft = self.placeholder_draft[language_code]

        if plugin_parent is not None:
            plugin_parent = plugin_parent.pk

        url = (
            "/{language_code}/admin/cms/page/add-plugin/"
            "?placeholder_id={placeholder_id}"
            "&plugin_type={plugin_type}"
            "&cms_path=%2Fde%2Ffoo_bar%2F" # Not important
            "&plugin_language={language_code}"
        ).format(
            language_code=language_code,
            placeholder_id=self.test_placeholder.pk,
            plugin_type=plugin_type,
        )
        if plugin_parent is not None:
            url += "&plugin_parent=%s" % plugin_parent

        user = self.login(usertype='superuser')

        print(url)
        response = self.client.get(url, HTTP_ACCEPT_LANGUAGE=language_code)
        if response.status_code == 302:
            url = response.url
            print("redirect url: %r" % url)

        pprint(post_data)
        response = self.client.post(url,
            data=post_data,
            HTTP_ACCEPT_LANGUAGE=language_code
        )
        if response.status_code == 302:
            self.assertRedirects(response, expected_url="FIXME")
        else:
            self.assertResponse(response,
                must_contain=(
                    '<div class="success"></div>',
                ),
                must_not_contain=("Traceback",),
                status_code=200,
                messages=[],
                template_name="admin/cms/page/plugin/confirm_form.html",
                html=False,
            )

        publish_page(self.test_page, user, language=language_code)

        self.client = Client() # "log out the user" e.g.: run assert_plugin() with anonymous

    def assert_plugin(self, language_code, must_contain_html=None, must_contain=None, template_name=None):
        if must_contain_html is None:
            must_contain_html = []

        if must_contain is None:
            must_contain = []

        url = self.test_page.get_absolute_url(language=language_code)
        response = self.client.get(url, HTTP_ACCEPT_LANGUAGE="en")
        self.assertResponse(response,
            must_contain=[
                "</html>",
            ] + list(must_contain),
            must_not_contain=(
                "Error", "Traceback",
            ),
            status_code=200,
            messages=[],
            template_name="tests/plugin_test.html",
            html=False,
        )
        self.assertResponse(response,
            must_contain=[
                "<title>CMS Plugin Test Page</title>",
            ] + list(must_contain_html),
            html=True,
        )
        if template_name is not None:
            self.assertTemplateUsed(response, template_name)
        return response # for more assertments

    def debug_response(self, response):
        content = response.content.decode("utf-8")
        print("*"*79)
        for line in content.splitlines():
            if line.strip():
                print(line)
        print("*"*79)

        # for copy&paste into test code:
        for line in content.splitlines():
            line=line.strip()
            if line:
                print("'%s'," % line)

        print("*"*79)



