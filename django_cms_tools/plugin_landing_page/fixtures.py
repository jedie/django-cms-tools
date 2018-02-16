
"""
    :create: 2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

from cms.api import add_plugin
from django.conf import settings
from django.utils import translation
from djangocms_text_ckeditor.cms_plugins import TextPlugin

from django_cms_tools.fixtures.pages import create_cms_plugin_page, CmsPageCreator
from django_cms_tools.plugin_landing_page.models import LandingPageModel

log = logging.getLogger(__name__)


def create_dummy_landing_pages(delete_first=False):
    language_code=settings.LANGUAGE_CODE
    with translation.override(language_code):

        if delete_first:
            queryset = LandingPageModel.objects.all()
            log.info("Delete %i LandingPageModel...", queryset.count())
            queryset.delete()

        qs = LandingPageModel.objects.language(language_code=language_code)

        for no in range(1,5):
            title="Dummy No. %i" % no
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
                    "<h3>dummy text part no. {no}</h3>\n"
                    "<p>Lorem ipsum dolor sit amet, consectetur adipisici elit, sed eiusmod tempor incidunt"
                    " ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud"
                    " exercitation ullamco laboris nisi ut aliquid ex ea commodi consequat. Quis aute"
                    " iure reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur."
                    " Excepteur sint obcaecat cupiditat non proident, sunt in culpa qui officia deserunt"
                    " mollit anim id est laborum.</p>"
                ).format(no = no)

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
    apphook='LandingPageApp'
    apphook_namespace='landingpage'

    placeholder_slots = () # Don't add any plugins

    def get_slug(self, language_code, lang_name):
        return "lp"


def create_landing_page_test_page(delete_first=False):
    # Create LandingPageApp page in all existing languages:

    plugin_page = LandingPageCmsPluginPageCreator(delete_first=delete_first).create()

    create_dummy_landing_pages(delete_first=delete_first)
