
"""
    :create: 2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, print_function, unicode_literals

import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models.fields import PlaceholderField

from parler.models import TranslatedFields
from publisher.models import PublisherParlerAutoSlugifyModel

# https://github.com/jedie/django-tools
from django_tools.models import UpdateTimeBaseModel

# Django CMS Tools
from django_cms_tools.permissions import EditModeAndChangePermissionMixin
from django_cms_tools.plugin_landing_page.cms_apps import get_landing_page_app
from django_cms_tools.plugin_landing_page.constants import LANDING_PAGE_PLACEHOLDER_NAME

log = logging.getLogger(__name__)


class LandingPageModel(EditModeAndChangePermissionMixin, UpdateTimeBaseModel, PublisherParlerAutoSlugifyModel):
    """
    fields from django_tools.models.UpdateTimeBaseModel:
        - createtime
        - lastupdatetime

    fields from publisher.models.PublisherParlerAutoSlugifyModel:
        - publisher_*
    """
    # TranslatedAutoSlugifyMixin options
    slug_source_field_name = "title"

    translations = TranslatedFields(
        title=models.CharField(_("Title"), max_length=234),
        slug=models.SlugField(
            verbose_name=_("Slug"),
            max_length=255,
            db_index=True,
            blank=True,
            help_text=_(
                "Used in the URL. If changed, the URL will change. "
                "Clear it to have it re-created automatically."),
        ),
    )
    robots_index = models.BooleanField(_("Robots-Index"), default=True,
        help_text=_("If checked: meta robots 'index' is set, otherwise 'noindex'.")
    )
    robots_follow = models.BooleanField(_("Robots-Follow"), default=True,
        help_text=_("If checked: meta robots 'follow' is set, otherwise 'nofollow'.")
    )

    content = PlaceholderField(LANDING_PAGE_PLACEHOLDER_NAME)

    def get_absolute_url(self, language=None):
        language = language or self.get_current_language()

        slug = self.safe_translation_getter('slug', language_code=language)
        if not slug:
            log.warning("Can't generate url: There is no slug.")
            return ""

        landing_page_app = get_landing_page_app()

        absolute_url = landing_page_app.get_absolute_url(
            view_path="landing_page-detail",
            reverse_kwargs={"slug": slug},
            language=language
        )
        return absolute_url

    def __str__(self):
        return "LandingPage %s" % self.get_absolute_url()

    class Meta(PublisherParlerAutoSlugifyModel.Meta):
        ordering = ("-createtime",)
        verbose_name = _("Landing Page")
        verbose_name_plural = _("Landing Pages")
