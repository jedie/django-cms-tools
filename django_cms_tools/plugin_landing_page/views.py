
"""
    :create: 2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

from cms.utils.urlutils import admin_reverse
from django.contrib.admin.options import IS_POPUP_VAR
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView

from cms.utils import get_language_from_request

from menus.utils import set_language_changer
from parler.views import TranslatableSlugMixin

# Django CMS Tools
from django_cms_tools.plugin_landing_page.app_settings import LANDING_PAGE_TOOLBAR_VERBOSE_NAME
from django_cms_tools.plugin_landing_page.constants import LANDING_PAGE_TOOLBAR_NAME, ADMIN_REVERSE_PREFIX
from django_cms_tools.plugin_landing_page.models import LandingPageModel

log = logging.getLogger(__name__)


class LandingPageDetailView(TranslatableSlugMixin, DetailView):
    model = LandingPageModel

    def get(self, request, *args, **kwargs):
        self.language = get_language_from_request(request)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.model.objects.active_translations(self.language)

        if not self.model.edit_mode_and_change_permission(self.request):
            log.info("Not in edit mode or User has no change permission: Display only 'public' items.")
            queryset = queryset.visible()
        else:
            log.info("edit mode is on and User has change permission: List only 'drafts' items.")
            queryset = queryset.drafts()

        return queryset

    def extend_toolbar(self, instance):
        menu = self.request.toolbar.get_or_create_menu(LANDING_PAGE_TOOLBAR_NAME, LANDING_PAGE_TOOLBAR_VERBOSE_NAME)
        menu.add_break()

        draft = instance.get_draft_object()
        url = admin_reverse(ADMIN_REVERSE_PREFIX + "_change", args=[draft.pk])
        url += "?%s" % urlencode({
            "language": self.language,
            # IS_POPUP_VAR: 1,
        })

        menu.add_modal_item(_('Change current Landing Page'), url=url)

    def get_object(self, queryset=None):
        instance = super().get_object(queryset=queryset)

        # Translate the slug while changing the language.
        set_language_changer(self.request, instance.get_absolute_url)

        # Append "edit current" link into toolbar menu
        self.extend_toolbar(instance)

        return instance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object: # LandingPageModel instance
            context["title"]=self.object.title
        return context

    def get_template_names(self):
        return ["landing_page/landing_page.html"]
