
"""
    :create: 2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext as _

from cms.admin.placeholderadmin import PlaceholderAdminMixin

from aldryn_translation_tools.admin import AllTranslationsMixin
from publisher.admin import PublisherParlerAdmin

# Django CMS Tools
from django_cms_tools.plugin_landing_page.models import LandingPageModel

log = logging.getLogger(__name__)


@admin.register(LandingPageModel)
class LandingPageAdmin(PlaceholderAdminMixin, AllTranslationsMixin, PublisherParlerAdmin):
    def view_on_page_link(self, obj):
        available_languages = obj.get_available_languages()

        html = "<ul>"
        for language_code, language_name in settings.LANGUAGES:
            if language_code in available_languages:
                url = obj.get_absolute_url(language=language_code)
                html += '<li>{lang}: <a href="{url}" target="_parent">{url}</a></li>'.format(
                    lang=language_code,
                    url=url,
                )
            else:
                html += '<li>{lang}: <i>{info}</i></li>'.format(
                    lang=language_code,
                    info=_("not translated")
                )
        html += "</ul>"
        return html

    view_on_page_link.allow_tags = True
    view_on_page_link.short_description = _("view on page")

    list_display = ("title", "visibility", "view_on_page_link")
    search_fields = (
        "translations__title",
    )
    fieldsets = (
        (None, {
            "fields": (
                ("title", "slug"),
            ),
        }),
        ("Meta", {
            "fields": (
                "robots_index",
                "robots_follow",
            ),
        }),
    )
