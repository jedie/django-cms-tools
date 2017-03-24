# coding: utf-8

from __future__ import unicode_literals, print_function

import pytest

from cms.models import Page

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.template import set_string_if_invalid, \
    TEMPLATE_INVALID_PREFIX
from django_tools.unittest_utils.unittest_base import BaseTestCase

from django_cms_tools.fixtures.pages import create_cms_index_pages


@pytest.mark.django_db
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
                "index in German",
            ),
            must_not_contain=("error", "Traceback"),
            status_code=200, html=False,
            browser_traceback=True
        )
        self.assertNotIn(TEMPLATE_INVALID_PREFIX, response.content.decode('utf8'))
