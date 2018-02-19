
"""
    :create: 2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

from django.contrib.admin.options import IS_POPUP_VAR
from django.urls import NoReverseMatch
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _

from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from cms.utils.urlutils import admin_reverse

# Django CMS Tools
from django_cms_tools.plugin_landing_page.app_settings import (
    LANDING_PAGE_ALWAYS_ADD_TOOLBAR, LANDING_PAGE_TOOLBAR_VERBOSE_NAME
)
from django_cms_tools.plugin_landing_page.cms_apps import get_landing_page_app
from django_cms_tools.plugin_landing_page.constants import ADMIN_REVERSE_PREFIX, LANDING_PAGE_TOOLBAR_NAME
from django_cms_tools.plugin_landing_page.models import LandingPageModel

log = logging.getLogger(__name__)


@toolbar_pool.register
class LandingPageToolbar(CMSToolbar):
    watch_models = [LandingPageModel]

    def populate(self):
        if LANDING_PAGE_ALWAYS_ADD_TOOLBAR or self.is_current_app:
            menu = self.toolbar.get_or_create_menu(LANDING_PAGE_TOOLBAR_NAME, LANDING_PAGE_TOOLBAR_VERBOSE_NAME)

            # app = get_landing_page_app()
            # app.add_view_on_page_toolbar_links(menu, current_lang=self.current_lang)

            user = self.request.user

            add_model_perm = LandingPageModel.has_add_permission(user, raise_exception=False)
            change_model_perm = LandingPageModel.has_change_permission(user, raise_exception=False)

            if change_model_perm:
                try:
                    url=admin_reverse(ADMIN_REVERSE_PREFIX + "_changelist")
                except NoReverseMatch as err:
                    log.error("Can't append 'admin change list link' to cms toolbar: %s" % err)
                else:
                    # url += "?%s" % urlencode({IS_POPUP_VAR: 1})
                    menu.add_sideframe_item(
                        name=_('change list'),
                        url=url,
                    )

            if add_model_perm:
                try:
                    url=admin_reverse(ADMIN_REVERSE_PREFIX + "_add")
                except NoReverseMatch as err:
                    log.error("Can't append 'admin add link' to cms toolbar: %s" % err)
                else:
                    # url += "?%s" % urlencode({IS_POPUP_VAR: 1})
                    menu.add_modal_item(
                        name=_('Add new Landing Page'),
                        url=url,
                    )
