
"""
    :create: 2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf import settings
from django.utils.translation import ugettext_lazy as _


# Template used to render one landing page:
LANDING_PAGE_TEMPLATE = getattr(settings, "LANDING_PAGE_TEMPLATE", "landing_page/landing_page.html")


# redirect user, e.g.: /en/langing_page/ -> /
LANDING_PAGE_HIDE_INDEX_VIEW = getattr(settings, "LANDING_PAGE_HIDE_INDEX_VIEW", True)


# Always expand toolbar or all links only if current page is the landing page app?
LANDING_PAGE_ALWAYS_ADD_TOOLBAR = getattr(settings, "LANDING_PAGE_ALWAYS_ADD_TOOLBAR", True)


# Menu Text in cms toolbar:
LANDING_PAGE_TOOLBAR_VERBOSE_NAME = getattr(settings, "LANDING_PAGE_TOOLBAR_VERBOSE_NAME", _("Landing Pages"))
