# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

import logging

import pytest

from django.utils import translation
from django.template.defaultfilters import slugify

from cms.api import create_page, create_title, add_plugin
from cms.constants import TEMPLATE_INHERITANCE_MAGIC
from cms.models import Page, CMSPlugin, settings, Title
from cms.utils import apphook_reload

from django_cms_tools.fixtures.languages import iter_languages

log = logging.getLogger(__name__)


class CmsPageCreator(object):
    """
    Create a normal Django CMS page
    """
    # Some defaults:
    languages = settings.LANGUAGES # Languages for created content.
    default_language_code = settings.LANGUAGE_CODE # First language to start create the page
    template = TEMPLATE_INHERITANCE_MAGIC
    in_navigation = True

    apphook = None
    apphook_namespace = None
    placeholder_slot = None

    def __init__(self, delete_first=False):
        self.delete_first = delete_first

        with translation.override(self.default_language_code):
            # for evaluate the language name lazy translation
            # e.g.: settings.LANGUAGE_CODE is not "en"

            self.default_lang_name = dict(self.languages)[self.default_language_code]
            self.slug = self.get_slug(self.default_language_code, self.default_lang_name)

    def get_title(self, language_code, lang_name):
        """
        :return: 'title' string for cms.api.create_page()
        """
        return "%s in %s" % (self.__class__.__name__, language_code)

    def get_slug(self, language_code, lang_name):
        """
        Notes:
            - slug must be unique!
            - slug is used to check if page already exists!
        :return: 'slug' string for cms.api.create_page()
        """
        title = self.get_title(language_code, lang_name)
        return slugify(title)

    def get_template(self, language_code, lang_name):
        """
        :return: 'template' string for cms.api.create_page()
        """
        return self.template

    def get_home_page(self):
        """
        Return the published home page.
        Used for 'parent' in cms.api.create_page()
        """
        try:
            home_page = Page.objects.get(is_home=True, publisher_is_draft=False)
        except Page.DoesNotExist:
            log.error('ERROR: "home page" doesn\'t exists!')
            raise RuntimeError('no home page')
        return home_page

    def get_parent_page(self):
        """
        For 'parent' in cms.api.create_page()
        """
        return None

    def publish(self, page):
        """
        Publish the page in all languages.
        """
        for language_code, lang_name in iter_languages(self.languages):
            # page = page.get_draft_object()
            url = page.get_absolute_url()

            if page.publisher_is_draft:
                page.publish(language_code)
                print('\tpage "%s" published in %s: %s' % (page, lang_name, url))
            else:
                print('\tpublished page "%s" already exists in %s: %s' % (page, lang_name, url))

    def create_page(self):
        """
        Create page (and page title) in default language
        """
        page = None

        if self.delete_first:
            pages = Page.objects.filter(title_set__slug=self.slug)
            log.debug("Delete %i pages...", pages.count())
            pages.delete()
        else:
            if self.apphook_namespace is not None:
                # Create a plugin page
                queryset = Page.objects.public()
                try:
                    page = queryset.get(application_namespace=self.apphook_namespace)
                except Page.DoesNotExist:
                    pass # Create page
                else:
                    log.debug("Use existing plugin page: %s", page)
                    return page
            else:
                # Not a plugin page
                queryset = Title.objects.filter(language=self.default_language_code)
                try:
                    title = queryset.filter(slug=self.slug).first()
                except Title.DoesNotExist:
                    pass # Create page
                else:
                    if title is not None:
                        log.debug("Use page from title with slug %r", self.slug)
                        page = title.page

        if page is None:
            with translation.override(self.default_language_code):
                # set right translation language
                # for evaluate language name lazy translation
                # e.g.: settings.LANGUAGE_CODE is not "en"

                page = create_page(
                    title=self.get_title(self.default_language_code, self.default_lang_name),
                    template=self.get_template(self.default_language_code, self.default_lang_name),
                    language=self.default_language_code,
                    slug=self.slug,
                    published=False,
                    parent=self.get_parent_page(),
                    in_navigation=self.in_navigation,
                    apphook=self.apphook,
                    apphook_namespace=self.apphook_namespace
                )
                log.debug("Page created in %s: %s", self.default_lang_name, page)
        else:
            # Get draft if existing page was found.
            page = page.get_draft_object()
        return page

    def create_title(self, page):
        """
        Create page title in all other languages with cms.api.create_title()
        """
        for language_code, lang_name in iter_languages(self.languages):
            try:
                title = Title.objects.get(page=page, language=language_code)
            except Title.DoesNotExist:
                title = create_title(
                    language=language_code,
                    title=self.get_title(language_code, lang_name),
                    page=page,
                    slug = self.get_slug(language_code, lang_name),
                )
                log.debug("Title created: %s", title)
            else:
                log.debug("Page title exist: %s", title)

    def fill_content(self, page):
        """
        Can be overwritten to add content to the created page
        """
        pass

    def create(self):
        page = self.create_page() # Create page (and page title) in default language
        self.create_title(page) # Create page title in all other languages
        self.fill_content(page) # Add content to the created page.
        self.publish(page) # Publish page in all languages

        # Force to reload the url configuration.
        # Important for unittests to "find" all plugins ;)
        apphook_reload.reload_urlconf()

        return page


@pytest.fixture()
def create_cms_index_pages(placeholder_slot="content"):
    """
    create cms home page and fill >content< placeholder with TextPlugin
    """
    try:
        Page.objects.get(is_home=True, publisher_is_draft=False)
    except Page.DoesNotExist:
        log.debug('Create index page in "en" and...')
        index_page = create_page(
            title="index in English",
            template=TEMPLATE_INHERITANCE_MAGIC,
            language=settings.LANGUAGE_CODE,
            published=False,
            in_navigation=True
        )
        placeholder, created = index_page.placeholders.get_or_create(slot=placeholder_slot)
        for language_code, lang_name in settings.LANGUAGES:
            with translation.override(language_code):
                title = 'index in %s' % lang_name
                print('\tcreate %r' % title)
                if language_code != settings.LANGUAGE_CODE:
                    create_title(language_code, title, index_page)
                add_plugin(
                    placeholder=placeholder,
                    plugin_type='TextPlugin', # djangocms_text_ckeditor
                    language=language_code,
                    body='index page in %s' % lang_name
                )
                index_page.publish(language_code)
    else:
        log.debug('Index page already exists.')



class CmsPluginPageCreator(CmsPageCreator):
    """
    Create a Django CMS plugin page and fill the content.
    Useable for default production fixtures or unittests fixtures.
    
    The idea is to inherit from this class and adpate it for your need by
    overwrite some methods ;)
    """
    def __init__(self, apphook, apphook_namespace, placeholder_slot, *args, **kwargs):
        self.apphook = apphook
        self.apphook_namespace = apphook_namespace
        self.placeholder_slot = placeholder_slot

        super(CmsPluginPageCreator, self).__init__(*args, **kwargs)

    def get_title(self, language_code, lang_name):
        """
        Contruct the page title. Called from self.create_title()
        """
        return '%s in %s' % (self.apphook, lang_name)

    def get_parent_page(self):
        """
        For 'parent' in cms.api.create_page()
        """
        return self.get_home_page()

    def get_add_plugin_kwargs(self, plugin_page, language_code, lang_name):
        """
        Return "content" for create the plugin.
        Called from self.add_plugins()
        """
        plugin_url = plugin_page.get_absolute_url(language=language_code)
        return {
            "plugin_type": 'TextPlugin', # djangocms_text_ckeditor
            "body": '<p><a href="{url}">{name}</a></p>'.format(
                url=plugin_url,
                name=self.apphook,
            )
        }

    def add_plugins(self, plugin_page, placeholder):
        """
        Add a "TextPlugin" in all languages.
        """
        for language_code, lang_name in iter_languages(self.languages):
            add_plugin_kwargs = self.get_add_plugin_kwargs(plugin_page, language_code, lang_name)

            print('\tcreate "%s" page in: %s' % (self.apphook, lang_name))
            add_plugin(
                placeholder=placeholder,
                language=language_code,
                **add_plugin_kwargs
            )

    def get_or_create_placeholder(self, plugin_page):
        """
        Add a placeholder if not exists.
        """
        placeholder, created = plugin_page.placeholders.get_or_create(
            slot=self.placeholder_slot
        )
        if created:
            log.debug("Create placeholder %r for %r", self.placeholder_slot, plugin_page)
        else:
            log.debug("Use existing placeholder %r for %r", self.placeholder_slot, plugin_page)
        return placeholder

    def fill_content(self, plugin_page):
        """
        Add a placeholder to the page.
        Here we add a "TextPlugin" in all languages. 
        """
        placeholder = self.get_or_create_placeholder(plugin_page)
        self.add_plugins(plugin_page, placeholder)

    def create(self):
        """
        Create the plugin page in all languages and fill dummy content.
        """
        plugin = CMSPlugin.objects.filter(plugin_type=self.apphook)
        if plugin.exists():
            log.debug('Plugin page for "%s" plugin already exist, ok.', self.apphook)
            raise plugin

        page = super(CmsPluginPageCreator, self).create()

        # Add a plugin with content in all languages to the created page.
        self.fill_content(page)

        return page


def create_cms_plugin_page(apphook, apphook_namespace, placeholder_slot="content"):
    """
    Create cms plugin page in all existing languages.
    Add a link to the index page.

    :param apphook: e.g...........: 'FooBarApp'
    :param apphook_namespace: e.g.: 'foobar'
    :return:
    """
    creator = CmsPluginPageCreator(
        apphook=apphook,
        apphook_namespace=apphook_namespace,
        placeholder_slot=placeholder_slot,
    )
    plugin_page = creator.create()
    return plugin_page
