
"""
    :create: 2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

from django.conf import settings
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from cms.api import add_plugin

from djangocms_text_ckeditor.cms_plugins import TextPlugin

# Django CMS Tools
from django_cms_tools.fixtures.languages import iter_languages
from django_cms_tools.fixtures.pages import CmsPageCreator, create_cms_plugin_page
from django_cms_tools.plugin_landing_page.models import LandingPageModel

log = logging.getLogger(__name__)


def create_dummy_landing_pages(delete_first=False):
    for language_code, lang_name in iter_languages(languages=None):
        if delete_first:
            queryset = LandingPageModel.objects.all()
            log.info("Delete %i LandingPageModel...", queryset.count())
            queryset.delete()

        qs = LandingPageModel.objects.language(language_code=language_code)

        for no in range(1,5):
            title="Dummy No. %i (%s)" % (no, language_code)
            instance, created = qs.get_or_create(
                publisher_is_draft=True,
                translations__language_code=language_code,
                translations__title=title,
            )
            if created:
                instance.title = title
                instance.slug = None
                instance.save()

                dummy_text = (
                    "<h3>dummy text part no. {no} in {lang_name}</h3>\n"
                    "<p>Lorem ipsum dolor sit amet, consectetur adipisici elit, sed eiusmod tempor incidunt"
                    " ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud"
                    " exercitation ullamco laboris nisi ut aliquid ex ea commodi consequat. Quis aute"
                    " iure reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur."
                    " Excepteur sint obcaecat cupiditat non proident, sunt in culpa qui officia deserunt"
                    " mollit anim id est laborum.</p>"
                ).format(
                    no = no,
                    lang_name = lang_name,
                )

                add_plugin(
                    placeholder=instance.content,
                    plugin_type=TextPlugin.__name__,
                    language=language_code,
                    body=dummy_text,
                )

                instance.publish()
                log.info("LandingPageMode created: %s", instance)
            else:
                log.info("Existing LandingPageMode: %s", instance)


class LandingPageCmsPluginPageCreator(CmsPageCreator):
    in_navigation = False # Don't display the landing page app in menu/sitemaps etc.
    apphook='LandingPageApp'
    apphook_namespace='landingpage'

    placeholder_slots = () # Don't add any plugins

    def __init__(self, *args, parent_page=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_page = parent_page

    def get_parent_page(self):
        return self.parent_page

    def get_title(self, language_code, lang_name):
        return _("Landing Pages")

    def get_slug(self, language_code, lang_name):
        return "lp"


def create_landing_page_test_page(delete_first=False, parent_page=None):
    # Create LandingPageApp page in all existing languages:

    plugin_page, created = LandingPageCmsPluginPageCreator(delete_first=delete_first, parent_page=parent_page).create()

    create_dummy_landing_pages(delete_first=delete_first)

    return plugin_page, created
