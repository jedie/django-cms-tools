# coding: utf-8

from __future__ import unicode_literals, print_function

import pytest

from cms.models import Page


class CmsPageTestUtilsMixin(object):
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
