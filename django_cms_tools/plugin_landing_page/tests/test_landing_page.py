
"""
    :create: 2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import pytest

from cms.models import Page, settings

from django_cms_tools.plugin_landing_page.models import LandingPageModel
from django_tools.unittest_utils.unittest_base import BaseTestCase

from django_cms_tools.fixtures.pages import create_cms_index_pages


class LandingPageTestBase(BaseTestCase):
    def test_urls(self):
        pages = Page.objects.public()
        urls = []
        for page in pages:
            for language_code, lang_name in settings.LANGUAGES:
                urls.append(page.get_absolute_url(language=language_code))

        self.assertEqual(urls, [
            "/de/", "/en/", "/fr/", # index pages
            "/de/landing_page/", "/en/landing_page/", "/fr/landing_page/" # landing_page pages
        ])

    def test_landing_page_urls(self):
        landing_pages = LandingPageModel.objects.all()
        urls = [landing_page.get_absolute_url(language="en") for landing_page in landing_pages]
        self.assertEqual(urls, [
            "/en/landing_page/a-landing_page-only-in-english/"
        ])

    def test_redirect_list_url(self):
        response = self.client.get("/en/landing_page/", HTTP_ACCEPT_LANGUAGE="en")
        self.assertRedirects(
            response, expected_url="/",
            status_code=301, # moved permanently
            fetch_redirect_response=False,
        )

    def test(self):
        response = self.client.get(
            "/en/landing_page/a-landing_page-only-in-english/",
            HTTP_ACCEPT_LANGUAGE="en"
        )
        self.assertResponse(response,
            must_contain=(
                "A landing_page only in English",
                "Placeholder text in english"
            ),
            must_not_contain=("Error",),
            template_name="landing_page/landing_page.html",
            status_code=200,
            html=False,
            browser_traceback=True
        )

        self.assertResponse(response,
            must_contain=(
                '<meta name="robots" content="noindex, follow">',
            ),
            html=True,
            browser_traceback=True
        )
