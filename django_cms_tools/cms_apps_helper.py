
"""
    :create: 2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

from cms.utils.i18n import force_language
from django.urls import reverse, NoReverseMatch
from django.utils.translation import ugettext_lazy as _

from cms.models import Page

log = logging.getLogger(__name__)


class CMSAppHelperMixin:
    """
    e.g.:

        @apphook_pool.register
        class FoobarApp(CMSAppHelperMixin, CMSConfigApp):
            app_name = "foobar"
            name = "Foobar"
            urls = ["foobar.urls"]
            app_config = FoobarConfig


        def get_foobar_app():
            app_name = FoobarApp.__name__ # FoobarApp
            apphook = apphook_pool.get_apphook(app_name=app_name)
            return apphook
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app_hook_name = "%sApp" % self.name  # e.g.: "FooApp"

    def get_app_page_url(self, language):
        app_page = self.get_app_page()
        return app_page.get_absolute_url(language=language)

    def get_absolute_url(self, view_path, reverse_kwargs, language):
        app_page = self.get_app_page()
        namespace = app_page.application_namespace

        with force_language(language):
            viewname = "%s:%s" % (namespace, view_path)
            try:
                return reverse(viewname, kwargs=reverse_kwargs)
            except NoReverseMatch as err:
                log.error("Can't reverse url: %s", err)
                return "#"

    def get_app_page(self):
        page_qs = Page.objects.public()
        app_page = page_qs.get(application_urls=self.app_hook_name)
        return app_page

    def add_view_on_page_toolbar_links(self, menu, current_lang):
        menu.add_link_item(
            name=_("View on Site"),
            url=self.get_app_page_url(language=current_lang),
        )
