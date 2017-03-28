# coding: utf-8

from __future__ import unicode_literals, print_function

import pytest

from cms.models import Page

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.template import set_string_if_invalid, \
    TEMPLATE_INVALID_PREFIX
from django_tools.unittest_utils.unittest_base import BaseTestCase

from django_cms_tools.fixtures.pages import create_cms_index_pages
from test_project.test_cms_plugin.fixtures import create_testapp_cms_plugin_page


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

    def test_index_link_en(self):
        self.assertResponse(
            self.client.get('/en/', HTTP_ACCEPT_LANGUAGE='en'),
            must_contain=(
                "<h1>Django-CMS-Tools Test Project</h1>",
                '<a href="/en/simpletestapp-in-english/">SimpleTestApp</a>',
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
                '<a href="/de/simpletestapp-in-deutsch/">SimpleTestApp</a>',
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

