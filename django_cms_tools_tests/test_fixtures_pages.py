# coding: utf-8

from __future__ import unicode_literals, print_function

import pytest

from cms.models import Page, settings, Title

from django.test import SimpleTestCase
from django.core.urlresolvers import resolve
from django.utils import translation

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.template import set_string_if_invalid, \
    TEMPLATE_INVALID_PREFIX
from django_tools.unittest_utils.unittest_base import BaseTestCase

from django_cms_tools.fixtures.languages import iter_languages
from django_cms_tools.fixtures.pages import create_cms_index_pages, \
    CmsPageCreator
from django_cms_tools.unittest_utils.page_mixins import CmsPageTestUtilsMixin
from django_cms_tools_test_project.test_cms_plugin.fixtures import \
    create_testapp_cms_plugin_page


class Unittests(SimpleTestCase):
    def test_iter_languages(self):
        codes = []
        names = []
        for language_code, lang_name in iter_languages(languages=None):
            # check if language is activated.
            self.assertEqual(translation.get_language(), language_code)
            codes.append(language_code)
            names.append("%s" % lang_name) # evaluate lazy translation

        self.assertEqual(codes, ["de", "en"])

        # Note: 'German' must be translated to 'Deutsch'
        self.assertEqual(names, ['Deutsch', 'English'])


@pytest.mark.usefixtures(
    create_cms_index_pages.__name__,
)
class ExistingCmsPageTests(BaseTestCase):
    def setUp(self):
        super(ExistingCmsPageTests, self).setUp()
        self.page = Page.objects.get(is_home=True, publisher_is_draft=False)

    def test_language_redirect_en(self):
        response = self.client.get('/', HTTP_ACCEPT_LANGUAGE='en')
        # debug_response(response)
        self.assertRedirects(response,
            expected_url='http://testserver/en/',
        )

    def test_language_redirect_de(self):
        response = self.client.get('/', HTTP_ACCEPT_LANGUAGE='de')
        # debug_response(response)
        self.assertRedirects(response,
            expected_url='http://testserver/de/',
        )

    def test_url_en(self):
        url = self.page.get_absolute_url(language="en")
        self.assertEqual(url, "/en/")

    def test_url_de(self):
        url = self.page.get_absolute_url(language="de")
        self.assertEqual(url, "/de/")

    @set_string_if_invalid()
    def test_request_en(self):
        response = self.client.get('/en/', HTTP_ACCEPT_LANGUAGE='en')
        # debug_response(response)
        self.assertResponse(response,
            must_contain=(
                "<h1>Django-CMS-Tools Test Project</h1>",
                "index in English",
            ),
            must_not_contain=("error", "Traceback"),
            status_code=200, html=False,
            browser_traceback=True
        )
        self.assertNotIn(TEMPLATE_INVALID_PREFIX, response.content.decode('utf8'))

    @set_string_if_invalid()
    def test_request_de(self):
        response = self.client.get('/de/', HTTP_ACCEPT_LANGUAGE='de')
        # debug_response(response)
        self.assertResponse(response,
            must_contain=(
                "<h1>Django-CMS-Tools Test Project</h1>",
                "index in Deutsch",
            ),
            must_not_contain=("error", "Traceback"),
            status_code=200, html=False,
            browser_traceback=True
        )
        self.assertNotIn(TEMPLATE_INVALID_PREFIX, response.content.decode('utf8'))


class PageTestFixture(CmsPageCreator):
    template='base.html'
    def get_title(self, language_code, lang_name):
        return "CreatePageTests() - %s" % lang_name

@pytest.fixture()
def empty_page_fixture():
    PageTestFixture().create()


@pytest.mark.usefixtures(
    empty_page_fixture.__name__
)
class CreatePageTests(CmsPageTestUtilsMixin, BaseTestCase):
    def assert_test_pages(self):
        self.assert_page_titles(
            language_code="en",
            reference=["CreatePageTests() - English"]
        )
        self.assert_page_titles(
            language_code="de",
            reference=["CreatePageTests() - Deutsch"]
        )
        self.assert_page_templates(
            reference=['base.html', 'base.html'],
            queryset=None # all pages (drafts + published)
        )
        self.assertEqual(Page.objects.all().count(), 2)

    def test_urls_en(self):
        self.assert_public_urls(language_code="en", reference=["/en/"])

    def test_urls_de(self):
        self.assert_public_urls(language_code="de", reference=["/de/"])

    def test_created_pages(self):
        self.assert_test_pages()

    def assert_changed_entries(self):
        self.assert_page_templates(reference=["foo.html", "foo.html"])
        self.assert_page_titles(language_code="en", reference=["bar"])
        self.assert_page_titles(language_code="de", reference=["bar"])

    def change_existing_entries(self):
        Page.objects.all().update(template="foo.html")
        Title.objects.all().update(title="bar")

    def test_dont_change_existing(self):
        self.change_existing_entries()
        self.assert_changed_entries()

        PageTestFixture(delete_first=False).create()

        self.assert_changed_entries() # Not changed?

    def test_delete_first(self):
        self.change_existing_entries()
        self.assert_changed_entries()

        PageTestFixture(delete_first=True).create()

        self.assert_test_pages() # recreated ?


@pytest.mark.usefixtures(
    create_cms_index_pages.__name__,
    create_testapp_cms_plugin_page.__name__,
)
class CreatePluginPageTests(BaseTestCase):
    """
    Tests for plugin page generation with:

        django_cms_tools.fixtures.pages.create_cms_plugin_page
    """
    def test_urls_en(self):
        pages = Page.objects.public()
        urls = [page.get_absolute_url(language="en") for page in pages]
        urls.sort()
        self.assertEqual(urls, ["/en/", "/en/simpletestapp-in-english/"])

    def test_urls_de(self):
        pages = Page.objects.public()
        urls = [page.get_absolute_url(language="de") for page in pages]
        urls.sort()
        self.assertEqual(urls, ["/de/", "/de/simpletestapp-in-deutsch/"])

    def test_url_resolve(self):
        url_data = {
            "/en/": "pages-root",
            "/de/": "pages-root",
            "/en/simpletestapp-in-english/": "test_cms_app",
            "/de/simpletestapp-in-deutsch/": "test_cms_app",
        }
        existing_lang_codes=[language_code for language_code, lang_name in settings.LANGUAGES]
        for url, url_name in url_data.items():
            language_code=url.split("/",2)[1]
            self.assertIn(language_code, existing_lang_codes)
            with translation.override(language_code):
                resolver_match = resolve(url)
                self.assertEqual(
                    resolver_match.url_name, url_name
                )

    def test_index_link_en(self):
        self.assertResponse(
            self.client.get('/en/', HTTP_ACCEPT_LANGUAGE='en'),
            must_contain=(
                "<h1>Django-CMS-Tools Test Project</h1>",
                '<a href="/en/">index in English</a>',
            ),
            must_not_contain=("error", "Traceback"),
            template_name='base.html',
            status_code=200, html=True,
            browser_traceback=True
        )

    def test_index_link_de(self):
        self.assertResponse(
            self.client.get('/de/', HTTP_ACCEPT_LANGUAGE='de'),
            must_contain=(
                "<h1>Django-CMS-Tools Test Project</h1>",
                '<a href="/de/">index in Deutsch</a>',
            ),
            must_not_contain=("error", "Traceback"),
            template_name='base.html',
            status_code=200, html=True,
            browser_traceback=True
        )

    def test_plugin_view_en(self):
        self.assertResponse(
            self.client.get('/en/simpletestapp-in-english/', HTTP_ACCEPT_LANGUAGE='en'),
            must_contain=(
                "<h1>Django-CMS-Tools Test Project</h1>",
                '<a href="/en/">index in English</a>', # cms menu link
                "<p>Hello World from the Simple CMS test App!</p>"
            ),
            must_not_contain=("error", "Traceback"),
            template_name='index_view.html',
            status_code=200, html=True,
            browser_traceback=True
        )

    def test_plugin_view_de(self):
        self.assertResponse(
            self.client.get('/de/simpletestapp-in-deutsch/', HTTP_ACCEPT_LANGUAGE='de'),
            must_contain=(
                "<h1>Django-CMS-Tools Test Project</h1>",
                '<a href="/de/">index in Deutsch</a>', # cms menu link
                "<p>Hello World from the Simple CMS test App!</p>"
            ),
            must_not_contain=("error", "Traceback"),
            template_name='index_view.html',
            status_code=200, html=True,
            browser_traceback=True
        )
