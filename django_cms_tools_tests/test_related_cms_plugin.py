# coding: utf-8

from __future__ import print_function, unicode_literals

from cms.models import Page

# https://github.com/jedie/django-tools
from django_tools.unittest_utils.unittest_base import BaseTestCase

# Django CMS Tools
from django_cms_tools.fixtures.pages import create_cms_index_pages
from django_cms_tools_test_project.test_cms_plugin.fixtures import create_related_plugin



class RelatedPluginTests(BaseTestCase):
    """
    Tests for from:

    django_cms_tools_test_project.test_cms_plugin.cms_plugin.RelatedPlugin
    """
    @classmethod
    def setUpTestData(cls):
        super(RelatedPluginTests, cls).setUpTestData()
        create_cms_index_pages()
        create_related_plugin()

    def test_urls_en(self):
        pages = Page.objects.public()
        urls = [page.get_absolute_url(language="en") for page in pages]
        urls.sort()
        self.assertEqual(urls, ["/en/", "/en/related-cms-plugin-test/"])

    def test_plugin_view_en(self):
        self.assertResponse(
            self.client.get('/en/related-cms-plugin-test/', HTTP_ACCEPT_LANGUAGE='en'),
            must_contain=(
                "<h1>Django-CMS-Tools Test Project</h1>",
                '<a href="/en/related-cms-plugin-test/">Related CMS Plugin Test</a>', # cms menu link
                "<ul>"
                "<li><p>CMS plugin entry no.: 1</p></li>"
                "<li><p>CMS plugin entry no.: 2</p></li>"
                "<li><p>CMS plugin entry no.: 3</p></li>"
                "<li><p>CMS plugin entry no.: 4</p></li>"
                "<li><p>CMS plugin entry no.: 5</p></li>"
                "<li><p>CMS plugin entry no.: 6</p></li>"
                "<li><p>CMS plugin entry no.: 7</p></li>"
                "</ul>"
            ),
            must_not_contain=("error", "Traceback"),
            template_name="related_cms_plugin.html",
            status_code=200,
            html=True,
            browser_traceback=True
        )
