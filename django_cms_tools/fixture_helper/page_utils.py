"""
    :created: 17.09.2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from cms.models import Page


def get_public_cms_app_namespaces():
    """
    :return: a tuple() with all cms app namespaces
    """
    qs = Page.objects.public()
    qs = qs.exclude(application_namespace=None)
    qs = qs.order_by('application_namespace')

    try:
        application_namespaces = list(
            qs.distinct('application_namespace').values_list(
                'application_namespace', flat=True))
    except NotImplementedError:
        # If SQLite used:
        #   DISTINCT ON fields is not supported by this database backend
        application_namespaces = list(
            set(qs.values_list('application_namespace', flat=True)))

    application_namespaces.sort()

    return tuple(application_namespaces)


def get_public_cms_page_urls(*, language_code):
    """
    :param language_code: e.g.: "en" or "de"
    :return: Tuple with all public urls in the given language
    """
    pages = Page.objects.public()
    urls = [page.get_absolute_url(language=language_code) for page in pages]
    urls.sort()
    return tuple(urls)
