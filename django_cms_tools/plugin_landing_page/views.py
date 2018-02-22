
"""
    :create: 2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

from cms.utils import get_language_from_request

from menus.utils import set_language_changer
from meta.views import MetadataMixin
from parler.views import TranslatableSlugMixin
from publisher_cms.views import PublisherCmsDetailView

# Django CMS Tools
from django_cms_tools.plugin_landing_page.app_settings import LANDING_PAGE_TOOLBAR_VERBOSE_NAME
from django_cms_tools.plugin_landing_page.constants import LANDING_PAGE_TOOLBAR_NAME
from django_cms_tools.plugin_landing_page.models import LandingPageModel

log = logging.getLogger(__name__)


class LandingPageDetailView(MetadataMixin, TranslatableSlugMixin, PublisherCmsDetailView):
    model = LandingPageModel

    # key and name of the "item" toolbar
    toolbar_key = LANDING_PAGE_TOOLBAR_NAME
    toolbar_verbose_name = LANDING_PAGE_TOOLBAR_VERBOSE_NAME

    def get(self, request, *args, **kwargs):
        self.language = get_language_from_request(request)
        return super().get(request, *args, **kwargs)

    def set_meta(self, instance):
        """
        Set django-meta stuff from LandingPageModel instance.
        """
        self.use_title_tag = True
        self.title = instance.title

    def get_object(self, queryset=None):
        instance = super().get_object(queryset=queryset)

        # Translate the slug while changing the language:
        set_language_changer(self.request, instance.get_absolute_url)

        # append publisher buttons:
        self.extend_toolbar(publisher_instance=instance)

        # Set django-meta stuff from LandingPageModel instance:
        self.set_meta(instance)

        return instance

    def get_template_names(self):
        return ["landing_page/landing_page.html"]
