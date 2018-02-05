# coding: utf-8

from __future__ import unicode_literals, print_function

from cms.models import Page, settings, Title

try:
    # https://pypi.org/project/python-slugify/
    from slugify import slugify
except ImportError:
    python_slugify = False
else:
    python_slugify = True

from django.test import SimpleTestCase
from django.core.urlresolvers import resolve
from django.utils import translation

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.template import set_string_if_invalid, \
    TEMPLATE_INVALID_PREFIX
from django_tools.unittest_utils.unittest_base import BaseTestCase

from django_cms_tools.fixtures.languages import iter_languages
from django_cms_tools.fixtures.pages import create_cms_index_pages, \
    CmsPageCreator, create_cms_plugin_page
from django_cms_tools.unittest_utils.page_mixins import CmsPageTestUtilsMixin
from django_cms_tools_test_project.test_cms_plugin.fixtures import \
    create_testapp_cms_plugin_page, ParentCmsPageCreator


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


class ExistingCmsPageTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        assert Page.objects.all().count() == 0
        create_cms_index_pages()
        assert Page.objects.all().count() == 2

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


class TwoSlotsPageCreator(CmsPageCreator):
    template='two_placeholder_slots.html'
    placeholder_slots = ("one", "two")


class CreatePageTests(CmsPageTestUtilsMixin, BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        assert Page.objects.all().count() == 0
        PageTestFixture().create()
        assert Page.objects.all().count() == 2

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
        self.assert_page_templates(reference=["other_template.html", "other_template.html"])
        self.assert_page_titles(language_code="en", reference=["bar"])
        self.assert_page_titles(language_code="de", reference=["bar"])

    def change_existing_entries(self):
        Page.objects.all().update(template="other_template.html")
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


class CreatePluginPageTests(BaseTestCase):
    """
    Tests for plugin page generation with:

        django_cms_tools.fixtures.pages.create_cms_plugin_page
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        assert Page.objects.all().count() == 0
        create_cms_index_pages()
        assert Page.objects.all().count() == 2
        create_testapp_cms_plugin_page()
        assert Page.objects.all().count() == 4

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


class CreateCMSPageTests(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        assert Page.objects.all().count() == 0
        create_cms_index_pages()
        assert Page.objects.all().count() == 2

    def test_urls_en(self):
        pages = Page.objects.public()
        urls = [page.get_absolute_url(language="en") for page in pages]
        urls.sort()
        self.assertEqual(urls, ["/en/"])

    def test_urls_de(self):
        pages = Page.objects.public()
        urls = [page.get_absolute_url(language="de") for page in pages]
        urls.sort()
        self.assertEqual(urls, ["/de/"])

    def test_other_parent_but_same_slug(self):
        home_page_draft = Page.objects.get(is_home=True, publisher_is_draft=True)

        page1, created = ParentCmsPageCreator(parent_page=home_page_draft).create()
        self.assertTrue(created)
        self.assertTrue(page1.publisher_is_draft, "not draft?!?")

        page2, created = ParentCmsPageCreator(parent_page=page1).create()
        self.assertTrue(created)
        self.assertTrue(page2.publisher_is_draft, "not draft?!?")

        page3, created = ParentCmsPageCreator(parent_page=page2).create()
        self.assertTrue(created)
        self.assertTrue(page3.publisher_is_draft, "not draft?!?")

        pages = Page.objects.public()
        pages = pages.order_by('id')
        urls = [page.get_absolute_url(language="en") for page in pages]

        if python_slugify:
            # https://pypi.org/project/python-slugify/
            reference = [
                '/en/',
                '/en/parent-test/',
                '/en/parent-test/parent-test/',
                '/en/parent-test/parent-test/parent-test/'
            ]
        else:
            # django.template.defaultfilters.slugify used:
            reference = [
                '/en/',
                '/en/parent_test/',
                '/en/parent_test/parent_test/',
                '/en/parent_test/parent_test/parent_test/'
            ]
        self.assertEqual(urls,reference)

        pks = [page.pk for page in pages]
        print(pks)
        self.assertEqual(pks,
            [
                home_page_draft.publisher_public.pk,
                page1.publisher_public.pk,
                page2.publisher_public.pk,
                page3.publisher_public.pk
            ]
        )
        self.assertLess(home_page_draft.publisher_public.pk, page1.publisher_public.pk)
        self.assertLess(page1.publisher_public.pk, page2.publisher_public.pk)
        self.assertLess(page2.publisher_public.pk, page3.publisher_public.pk)

    def test_double_detection(self):
        home_page_draft = Page.objects.get(is_home=True, publisher_is_draft=True)

        page1, created = ParentCmsPageCreator(parent_page=home_page_draft).create()
        self.assertTrue(created)
        self.assertTrue(page1.publisher_is_draft, "not draft?!?")

        # same parent and same slug should be not created:
        page2, created = ParentCmsPageCreator(parent_page=home_page_draft).create()
        self.assertEqual(page1.pk, page2.pk)
        self.assertFalse(created)

    def test_create_two_placeholders(self):
        page, created = TwoSlotsPageCreator().create()
        self.assertTrue(created)

        url = page.get_absolute_url(language="en")
        self.assertEqual(url, "/en/twoslotspagecreator-in-en/")

        self.assertResponse(
            self.client.get(url, HTTP_ACCEPT_LANGUAGE="en"),
            must_contain=(
                "<h1>Django-CMS-Tools Test Project</h1>",
                "<h2>Dummy no. 1 in English (placeholder one)</h2>",
                "<h2>Dummy no. 1 in English (placeholder two)</h2>",
            ),
            must_not_contain=("error", "Traceback"),
            template_name='two_placeholder_slots.html',
            status_code=200, html=True,
            browser_traceback=True
        )

    def test_create_cms_plugin_page(self):
        create_cms_plugin_page(
            apphook='SimpleTestApp',
            apphook_namespace='simpletest',
            placeholder_slot=None
        )
        pages = Page.objects.public()
        urls = [page.get_absolute_url(language="en") for page in pages]
        urls.sort()
        self.assertEqual(urls, ["/en/", "/en/simpletestapp-in-english/"])
