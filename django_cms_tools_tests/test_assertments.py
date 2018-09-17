"""
    :created: 17.09.2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.unittest_base import BaseTestCase
from django_tools.unittest_utils.user import TestUserMixin

# Django CMS Tools
from django_cms_tools.fixture_helper.pages import create_cms_index_pages
from django_cms_tools.plugin_landing_page.fixtures import create_landing_page_test_page
from django_cms_tools.unittest_utils.assertments import assert_public_cms_app_namespaces, assert_public_cms_page_urls


class AssertmentsTestCase(TestUserMixin, BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        index_page, created = create_cms_index_pages()
        create_landing_page_test_page(parent_page=index_page)

    def test_assert_public_cms_app_namespaces(self):
        assert_public_cms_app_namespaces(cms_app_namespaces=["landingpage"])

    def test_assert_public_cms_app_namespaces_failed(self):
        self.assertRaises(
            AssertionError,
            assert_public_cms_app_namespaces,
            cms_app_namespaces=["not there"])

    def test_assert_public_cms_page_urls(self):
        assert_public_cms_page_urls(language_code="de", urls=["/de/lp/"])
        assert_public_cms_page_urls(language_code="en", urls=["/en/lp/"])

    def test_assert_public_cms_page_urls_failed(self):
        self.assertRaises(
            AssertionError,
            assert_public_cms_page_urls,
            language_code="de",
            urls=["/not/here/"])

    def test_assert_public_cms_page_urls_wrong_language(self):
        self.assertRaises(
            AssertionError,
            assert_public_cms_page_urls,
            language_code="XX",
            urls=["/de/lp/"])
