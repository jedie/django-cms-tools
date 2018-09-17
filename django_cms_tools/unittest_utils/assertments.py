"""
    :created: 17.09.2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf import settings

# Django CMS Tools
from django_cms_tools.fixture_helper.page_utils import get_public_cms_app_namespaces, get_public_cms_page_urls


def assert_language_code(*, language_code):
    """
    Check if given language_code is in settings.LANGUAGES
    """
    existing_language_codes = tuple(dict(settings.LANGUAGES).keys())
    assert language_code in existing_language_codes, "%r not in settings.LANGUAGES=%r" % (
        language_code, settings.LANGUAGES)


def assert_public_cms_app_namespaces(*, cms_app_namespaces):
    """
    Check if given namespaces exists.
    """
    assert isinstance(cms_app_namespaces, (list, tuple))
    existing_namespaces = get_public_cms_app_namespaces()
    for cms_app_namespace in cms_app_namespaces:
        assert cms_app_namespace in existing_namespaces, "Namespace %r not found in: %r" % (
            cms_app_namespace, existing_namespaces)


def assert_public_cms_page_urls(*, language_code, urls):
    """
    Check if given urls exist.
    """
    assert_language_code(language_code=language_code)
    assert isinstance(urls, (list, tuple))

    existing_urls = get_public_cms_page_urls(language_code=language_code)
    for url in urls:
        assert url in existing_urls, "%r not in %r" % (url, existing_urls)
