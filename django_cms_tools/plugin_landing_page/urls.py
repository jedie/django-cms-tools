
"""
    :create: 2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.conf.urls import url
from django.views.generic import RedirectView

# Django CMS Tools
from django_cms_tools.plugin_landing_page.app_settings import LANDING_PAGE_HIDE_INDEX_VIEW
from django_cms_tools.plugin_landing_page.views import LandingPageDetailView


if LANDING_PAGE_HIDE_INDEX_VIEW:
    urlpatterns = [
        url(r"^$", RedirectView.as_view(url="/", permanent=True)), # e.g.: /en/langing_page/ -> /
    ]
else:
    urlpatterns = []


urlpatterns += [
    url(r"^(?P<slug>\w[-\w]*)/$", LandingPageDetailView.as_view(), name="landing_page-detail"),
]
