
"""
    :create: 2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from cms.models import Page, settings

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.unittest_base import BaseTestCase
from django_tools.unittest_utils.user import TestUserMixin

# Django CMS Tools
from django_cms_tools.fixtures.pages import create_cms_index_pages
from django_cms_tools.plugin_landing_page import app_settings
from django_cms_tools.plugin_landing_page.fixtures import create_landing_page_test_page
from django_cms_tools.plugin_landing_page.models import LandingPageModel


class LandingPageTest(TestUserMixin, BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        assert Page.objects.all().count() == 0
        assert LandingPageModel.objects.count() == 0

        index_page, created = create_cms_index_pages()
        assert Page.objects.all().count() == 2

        cls.plugin_page, created = create_landing_page_test_page(parent_page=index_page)
        assert Page.objects.all().count() == 4
        assert LandingPageModel.objects.count() == 16  # 4 dummies * 2 languages * 2 public/draft

        cls.url_en = cls.plugin_page.get_absolute_url(language="en")
        cls.url_de = cls.plugin_page.get_absolute_url(language="de")

        cls.landing_page_2_en = LandingPageModel.objects.language(language_code="en").published().get(
            translations__language_code="en",
            translations__slug="dummy-no-2-en",
        )
        cls.landing_page_2_en_url = cls.landing_page_2_en.get_absolute_url(language="en")

    def test_setUp(self):
        self.assertEqual(self.url_en, "/en/lp/")
        self.assertEqual(self.url_de, "/de/lp/")
        self.assertEqual(self.landing_page_2_en.slug, "dummy-no-2-en")
        self.assertEqual(self.landing_page_2_en.is_published, True)
        self.assertEqual(self.landing_page_2_en.is_visible, True)
        self.assertEqual(self.landing_page_2_en_url, "/en/lp/dummy-no-2-en/")

    def test_urls(self):
        pages = Page.objects.public()
        urls = []
        for page in pages:
            for language_code, lang_name in settings.LANGUAGES:
                urls.append(page.get_absolute_url(language=language_code))

        self.assertEqual(urls, [
            "/de/", "/en/", # index pages
            "/de/lp/", "/en/lp/" # landing_page pages
        ])

    def test_landing_page_urls(self):
        landing_pages = LandingPageModel.objects.published()
        urls = [landing_page.get_absolute_url(language="en") for landing_page in landing_pages]
        urls.sort()
        print(urls)
        self.assertEqual(urls, [
            "/en/lp/dummy-no-1-de/",
            "/en/lp/dummy-no-1-en/",
            "/en/lp/dummy-no-2-de/",
            "/en/lp/dummy-no-2-en/",
            "/en/lp/dummy-no-3-de/",
            "/en/lp/dummy-no-3-en/",
            "/en/lp/dummy-no-4-de/",
            "/en/lp/dummy-no-4-en/"
        ])

    def test_redirect_list_url(self):
        # Depend on settings.LANDING_PAGE_HIDE_INDEX_VIEW
        self.assertEqual(app_settings.LANDING_PAGE_HIDE_INDEX_VIEW, True)

        response = self.client.get("/en/lp/", HTTP_ACCEPT_LANGUAGE="en")
        self.assertRedirects(
            response, expected_url="/",
            status_code=301, # moved permanently
            fetch_redirect_response=False,
        )

    def test_landing_page_view(self):
        response = self.client.get("/en/lp/dummy-no-2-en/", HTTP_ACCEPT_LANGUAGE="en")
        self.assertResponse(response,
            must_contain=(
                "<title>Dummy No. 2 (en)</title>",
                "Django-CMS-Tools Test Project",
                "dummy text part no. 2 in English",
                "Lorem ipsum dolor sit amet",
            ),
            must_not_contain=("Error",),
            template_name="landing_page/landing_page.html",
            status_code=200,
            html=False,
            browser_traceback=True
        )

    def test_robot(self):
        qs = LandingPageModel.objects.language(language_code="en")
        landing_page = qs.get(
            publisher_is_draft=True,
            translations__language_code="en",
            translations__slug="dummy-no-3-en",
        )


        # check the default "index, follow":

        public = landing_page.get_public_object()
        self.assertEqual(public.robots_index, True)
        self.assertEqual(public.robots_follow, True)

        response = self.client.get("/en/lp/dummy-no-3-en/", HTTP_ACCEPT_LANGUAGE="en")
        self.assertResponse(response,
            must_contain=(
                '<title>Dummy No. 3 (en)</title>',
                '<meta name="robots" content="index, follow">',
            ),
            must_not_contain=("Error",),
            template_name="landing_page/landing_page.html",
            messages=[],
            status_code=200,
            html=True,
            browser_traceback=True
        )


        # check 'noindex':

        landing_page.robots_index = False
        landing_page.save()
        landing_page.publish()

        public = landing_page.get_public_object()
        self.assertEqual(public.robots_index, False)
        self.assertEqual(public.robots_follow, True)

        response = self.client.get("/en/lp/dummy-no-3-en/", HTTP_ACCEPT_LANGUAGE="en")
        self.assertResponse(response,
            must_contain=(
                '<title>Dummy No. 3 (en)</title>',
                '<meta name="robots" content="noindex, follow">',
            ),
            must_not_contain=("Error",),
            template_name="landing_page/landing_page.html",
            messages=[],
            status_code=200,
            html=True,
            browser_traceback=True
        )


        # check 'nofollow'

        landing_page.robots_index = True
        landing_page.robots_follow = False
        landing_page.save()
        landing_page.publish()

        public = landing_page.get_public_object()
        self.assertEqual(public.robots_index, True)
        self.assertEqual(public.robots_follow, False)

        response = self.client.get("/en/lp/dummy-no-3-en/", HTTP_ACCEPT_LANGUAGE="en")
        self.assertResponse(response,
            must_contain=(
                '<title>Dummy No. 3 (en)</title>',
                '<meta name="robots" content="index, nofollow">',
            ),
            must_not_contain=("Error",),
            template_name="landing_page/landing_page.html",
            messages=[],
            status_code=200,
            html=True,
            browser_traceback=True
        )

    def test_toolbar_links_no_edit_mode(self):
        self.login(usertype='superuser')

        response = self.client.get("/en/lp/dummy-no-2-en/", HTTP_ACCEPT_LANGUAGE="en")
        self.assertResponse(response,
            must_contain=(
                '<title>Dummy No. 2 (en)</title>',
                'Double-click to edit',
                'Logout superuser',

                'change list',
                'href="/en/admin/plugin_landing_page/landingpagemodel/"',

                'Add new Landing Page...',
                'href="/en/admin/plugin_landing_page/landingpagemodel/add/"',
            ),
            must_not_contain=(
                "Error",
                'Change &#39;Landing Page&#39; in admin...', # The Link will be not added in edit mode!
            ),
            template_name="landing_page/landing_page.html",
            messages=[],
            status_code=200,
            html=False,
            browser_traceback=True
        )

    def test_toolbar_links_edit_mode(self):
        self.login(usertype='superuser')

        change_url = "/en/admin/plugin_landing_page/landingpagemodel/%i/change/?language=en" % (
            self.landing_page_2_en.get_draft_object().pk
        )

        response = self.client.get("/en/lp/dummy-no-2-en/?edit", HTTP_ACCEPT_LANGUAGE="en")
        self.assertResponse(response,
            must_contain=(
                '<title>Dummy No. 2 (en)</title>',
                'Double-click to edit',
                'Logout superuser',

                'change list',
                'href="/en/admin/plugin_landing_page/landingpagemodel/"',

                'Add new Landing Page...',
                'href="/en/admin/plugin_landing_page/landingpagemodel/add/"',

                'href="%s"' % change_url,
                'Change &#39;Landing Page&#39; in admin...',
            ),
            must_not_contain=("Error",),
            template_name="landing_page/landing_page.html",
            messages=[],
            status_code=200,
            html=False,
            browser_traceback=True
        )

    def test_add_new_langing_page(self):
        self.login(usertype='superuser')

        LandingPageModel.objects.all().delete()

        response = self.client.post(
            path="/en/admin/plugin_landing_page/landingpagemodel/add/?language=en",
            data={
                "title": "a new langing page",
                "robots_index": "on",
                "robots_follow": "on",
                "_save_published": "Save and Publish",
            },
            HTTP_ACCEPT_LANGUAGE="en"
        )
        self.assertRedirects(response,
            expected_url="/en/admin/plugin_landing_page/landingpagemodel/",
            status_code=302,
            fetch_redirect_response=False
        )

        self.assertEqual(LandingPageModel.objects.count(), 2)  # draft+published

        landing_page = LandingPageModel.objects.published()[0]
        self.assertEqual(landing_page.title, "a new langing page")

