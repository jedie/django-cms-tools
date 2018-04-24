
from django.conf import settings
from django.contrib import auth
from django.utils import translation

from cms.models import Page


class CmsPageTestUtilsMixin(object):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.UserModel = auth.get_user_model()

    def setUp(self):
        super().setUp()

        # activate english for tests as default
        translation.activate("en")
        assert "en" in dict(settings.LANGUAGES), "Check: %s" % repr(settings.LANGUAGES)

    def get_public_urls(self, language_code):
        pages = Page.objects.public()
        urls = [page.get_absolute_url(language=language_code) for page in pages]
        urls.sort()
        return urls

    def assert_public_urls(self, language_code, reference):
        urls = self.get_public_urls(language_code)
        self.assertEqual(urls, reference)

    def get_page_titles(self, language_code):
        pages = Page.objects.public()
        titles = [page.get_page_title(language=language_code) for page in pages]
        return titles

    def assert_page_titles(self, language_code, reference):
        titles = self.get_page_titles(language_code)
        self.assertEqual(titles, reference)

    def assert_page_templates(self, reference, queryset=None):
        """
        Compare page templates

        :param reference: List of template names
        :param queryset: Page queryset, if None: all pages (drafts + published)
        """
        if queryset is None:
            queryset = Page.objects.all()

        for no, page in enumerate(queryset):
            first = page.template
            second = reference[no]

            self.assertEqual(first, second,
                "Page '%s' has a wrong template: %r != %r" % (page, first, second)
            )

    def force_login(self, username):
        try:
            user = self.UserModel.objects.get(username=username)
        except self.UserModel.DoesNotExist as err:
            print("ERROR: %s" % err)
            print("Existing users are:", self.UserModel.objects.all())
            raise

        assert user.is_active
        self.client.force_login(user)
        return user

    def get_test_page(self, slug, language_code=None):
        if language_code is None:
            language_code = settings.LANGUAGE_CODE

        qs = Page.objects.public()
        qs = qs.filter(
            title_set__slug=slug,
            title_set__language=language_code,
        )
        try:
            page = qs[0]
        except IndexError as err:
            print("\nERROR: Can't find page slug:%r language: %r" % (slug, language_code))
            print("Origin error: %s" % err)

            print("\nAll urls:")
            urls = [page.get_absolute_url(language=language_code) for page in Page.objects.public()]
            print("\n".join(urls))
            raise

        return page
