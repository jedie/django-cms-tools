
"""
    :create: 2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

# Django CMS Tools
from django_cms_tools.cms_apps_helper import CMSAppHelperMixin
from django_cms_tools.plugin_landing_page.constants import (
    LANDING_PAGE_APP_NAME, LANDING_PAGE_APPHOOK_NAMESPACE, LANDING_PAGE_URLS
)

log = logging.getLogger(__name__)


@apphook_pool.register
class LandingPageApp(CMSAppHelperMixin, CMSApp):
    """
    ./manage.py cms_page_info application_urls application_namespace navigation_extenders
    """
    name = LANDING_PAGE_APPHOOK_NAMESPACE  # name of the apphook (required)
    app_name = LANDING_PAGE_APP_NAME  # name of the app, this enables Django namespaces support

    urls = [LANDING_PAGE_URLS]

assert LandingPageApp.__name__.startswith(LANDING_PAGE_APPHOOK_NAMESPACE)


def get_landing_page_app():
    class_name = LandingPageApp.__name__ # "LandingPageApp"
    app = apphook_pool.get_apphook(app_name=class_name)
    return app
