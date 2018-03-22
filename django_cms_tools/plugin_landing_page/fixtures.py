
"""
    :create: 2018 by Jens Diemer
    :copyleft: 2018 by the django-cms-tools team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

from django.conf import settings
from django.utils import translation
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from cms.api import add_plugin

from djangocms_text_ckeditor.cms_plugins import TextPlugin
from publisher.models import PublisherModelBase

# Django CMS Tools
from django_cms_tools.fixtures.languages import iter_languages
from django_cms_tools.fixtures.pages import CmsPageCreator, create_cms_plugin_page
from django_cms_tools.plugin_landing_page.models import LandingPageModel

log = logging.getLogger(__name__)


class ParlerDummyGenerator:
    languages = settings.LANGUAGES # Languages for created content.
    default_language_code = settings.LANGUAGE_CODE # First language to start create

    def __init__(self, ParlerModelClass, publisher_model=False, unique_translation_field="slug"):
        self.ParlerModelClass = ParlerModelClass
        self.class_name = ParlerModelClass.__name__
        self.publisher_model = publisher_model # ParlerModelClass is sub class from PublisherModelBase) ?
        self.unique_translation_field = unique_translation_field

    def get_unique_translation_field_value(self, no, language_code):
        return slugify(
            "%s %s %i" % (self.class_name, language_code, no)
        )

    def add_instance_values(self, instance, language_code, lang_name, no):
        return instance

    def _get_lookup_kwargs(self, language_code, translation_field_value):
        lookup_kwargs = {
            "translations__language_code": language_code,
            "translations__%s" % self.unique_translation_field: translation_field_value
        }
        if self.publisher_model:
            # Is a Publisher model: filter drafts only:
            lookup_kwargs["publisher_is_draft"] = True

        return lookup_kwargs

    def get_or_create(self, count):
        for no in range(1,count+1):
            self._get_or_create(no=no)

    def _get_or_create(self, no):
        translation_field_value = self.get_unique_translation_field_value(no, language_code=self.default_language_code)

        lookup_kwargs = self._get_lookup_kwargs(
            language_code=self.default_language_code,
            translation_field_value=translation_field_value
        )

        qs = self.ParlerModelClass.objects.language(language_code=self.default_language_code)
        instance, created = qs.get_or_create(**lookup_kwargs)
        if created:
            log.info(" *** New %r (no:%i) created.", self.class_name, no)
        else:
            log.info(" *** Use existing %r (no:%i) instance.", self.class_name, no)

        for language_code, lang_name in iter_languages(languages=None):
            log.info("Add %r instance values", language_code)
            instance.set_current_language(language_code)
            translation_field_value = self.get_unique_translation_field_value(no, language_code)
            setattr(instance, self.unique_translation_field, translation_field_value)
            self.add_instance_values(instance, language_code, lang_name, no)

        log.info("Save no.%i: %r", no, instance)
        instance.save()
        if self.publisher_model:
            log.info("Publish no.%i: %r", no, instance)
            instance.publish()



class DummyLandingPageGenerator(ParlerDummyGenerator):
    def add_instance_values(self, instance, language_code, lang_name, no):
        instance.title = "LandingPage dummy No. %i (%s)" % (no, language_code)
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
        return instance




def create_dummy_landing_pages(delete_first=False):
    DummyLandingPageGenerator(
        ParlerModelClass=LandingPageModel,
        publisher_model=True,
        unique_translation_field="slug"
    ).get_or_create(count=5)


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
