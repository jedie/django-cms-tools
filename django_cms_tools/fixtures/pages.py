# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals

import logging

import pytest

from django.utils import translation

try:
    # https://pypi.org/project/python-slugify/
    from slugify import slugify
except ImportError:
    from django.template.defaultfilters import slugify

from cms.api import create_page, create_title, add_plugin
from cms.constants import TEMPLATE_INHERITANCE_MAGIC
from cms.models import Page, CMSPlugin, settings, Title
from cms.utils import apphook_reload

from django_cms_tools.fixtures.languages import iter_languages

log = logging.getLogger(__name__)


def get_or_create_placeholder(page, placeholder_slot, delete_existing=False):
    """
    Get or create a placeholder on the given page.
    Optional: Delete existing placeholder.
    """
    placeholder, created = page.placeholders.get_or_create(
        slot=placeholder_slot
    )
    if created:
        log.debug("Create placeholder %r for page %r", placeholder_slot, page.get_title())
    else:
        log.debug("Use existing placeholder %r for page %r", placeholder_slot, page.get_title())

    if delete_existing:
        queryset = CMSPlugin.objects.all().filter(placeholder = placeholder)
        log.info("Delete %i CMSPlugins on placeholder %s...", queryset.count(), placeholder)
        queryset.delete()

    return placeholder, created


def publish_page(page, languages):
    """
    Publish a CMS page in all given languages.
    """
    for language_code, lang_name in iter_languages(languages):
        url = page.get_absolute_url()

        if page.publisher_is_draft:
            page.publish(language_code)
            log.info('page "%s" published in %s: %s', page, lang_name, url)
        else:
            log.info('published page "%s" already exists in %s: %s', page, lang_name, url)
    return page.reload()


class CmsPageCreator(object):
    """
    Create a normal Django CMS page
    """
    # Some defaults:
    languages = settings.LANGUAGES # Languages for created content.
    default_language_code = settings.LANGUAGE_CODE # First language to start create the page
    template = TEMPLATE_INHERITANCE_MAGIC
    in_navigation = True
    apphook = None            # e.g.: "FooBarApp"
    apphook_namespace = None  # e.g.: "foobar"
    placeholder_slots = ("content",)

    dummy_text_count = 3

    prefix_dummy_part = "<h2>Dummy no. {no} in {lang_name} (placeholder {slot})</h2>"
    dummy_text_part = (
        "<h3>dummy text part no. {no} in placeholder {slot}</h3>\n"
        "<p>Lorem ipsum dolor sit amet, consectetur adipisici elit, sed eiusmod tempor incidunt"
        " ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud"
        " exercitation ullamco laboris nisi ut aliquid ex ea commodi consequat. Quis aute"
        " iure reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur."
        " Excepteur sint obcaecat cupiditat non proident, sunt in culpa qui officia deserunt"
        " mollit anim id est laborum.</p>"
    )
    suffix_dummy_part = "<p>(absolute url: {absolute_url})</p>"

    def __init__(self, delete_first=False, placeholder_slots=None):
        self.delete_first = delete_first

        if placeholder_slots is not None:
            self.placeholder_slots = placeholder_slots

    def get_title(self, language_code, lang_name):
        """
        :return: 'title' string for cms.api.create_page()
        """
        return "%s in %s" % (self.__class__.__name__, language_code)

    def get_menu_title(self, language_code, lang_name):
        """
        :return: 'menu_title' string for cms.api.create_page()
        """
        return None # No extra title for menu

    def get_slug(self, language_code, lang_name):
        """
        Notes:
            - slug must be unique!
            - slug is used to check if page already exists!
        :return: 'slug' string for cms.api.create_page()
        """
        title = self.get_title(language_code, lang_name)
        assert title != ""

        title = str(title) # e.g.: evaluate a lazy translation

        slug = slugify(title)
        assert slug != "", "Title %r results in empty slug!" % title
        return slug

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
            home_page_draft = Page.objects.get(is_home=True, publisher_is_draft=True)
        except Page.DoesNotExist:
            log.error('ERROR: "home page" doesn\'t exists!')
            raise RuntimeError('no home page')
        return home_page_draft

    def get_parent_page(self):
        """
        For 'parent' in cms.api.create_page()
        """
        return None

    def publish(self, page):
        """
        Publish the page in all languages.
        """
        assert page.publisher_is_draft==True, "Page '%s' must be a draft!" % page
        publish_page(page, languages=self.languages)

    def create_page(self, **extra_kwargs):
        """
        Create page (and page title) in default language

        extra_kwargs will be pass to cms.api.create_page()
        e.g.:
            extra_kwargs={
                "soft_root": True,
                "reverse_id": my_reverse_id,
            }
        """
        with translation.override(self.default_language_code):
            # for evaluate the language name lazy translation
            # e.g.: settings.LANGUAGE_CODE is not "en"

            self.default_lang_name = dict(self.languages)[self.default_language_code]
            self.slug = self.get_slug(self.default_language_code, self.default_lang_name)
            assert self.slug != ""

        page = None
        parent=self.get_parent_page()
        if parent is not None:
            assert parent.publisher_is_draft==True, "Parent page '%s' must be a draft!" % parent

        if self.delete_first:
            if self.apphook_namespace is not None:
                pages = Page.objects.filter(
                    application_namespace=self.apphook_namespace,
                    parent=parent,
                )
            else:
                pages = Page.objects.filter(
                    title_set__slug=self.slug,
                    parent=parent,
                )
            log.debug("Delete %i pages...", pages.count())
            pages.delete()
        else:
            if self.apphook_namespace is not None:
                # Create a plugin page
                queryset = Page.objects.drafts()
                queryset = queryset.filter(parent=parent)
                try:
                    page = queryset.get(application_namespace=self.apphook_namespace)
                except Page.DoesNotExist:
                    pass # Create page
                else:
                    log.debug("Use existing page: %s", page)
                    created=False
                    return page, created
            else:
                # Not a plugin page
                queryset = Title.objects.filter(language=self.default_language_code)
                queryset = queryset.filter(page__parent=parent)
                try:
                    title = queryset.filter(slug=self.slug).first()
                except Title.DoesNotExist:
                    pass # Create page
                else:
                    if title is not None:
                        log.debug("Use page from title with slug %r", self.slug)
                        page = title.page
                        created=False

        if page is None:
            with translation.override(self.default_language_code):
                # set right translation language
                # for evaluate language name lazy translation
                # e.g.: settings.LANGUAGE_CODE is not "en"

                page = create_page(
                    title=self.get_title(self.default_language_code, self.default_lang_name),
                    menu_title=self.get_menu_title(self.default_language_code, self.default_lang_name),
                    template=self.get_template(self.default_language_code, self.default_lang_name),
                    language=self.default_language_code,
                    slug=self.slug,
                    published=False,
                    parent=parent,
                    in_navigation=self.in_navigation,
                    apphook=self.apphook,
                    apphook_namespace=self.apphook_namespace,
                    **extra_kwargs
                )
                created=True
                log.debug("Page created in %s: %s", self.default_lang_name, page)

        assert page.publisher_is_draft==True
        return page, created

    def create_title(self, page):
        """
        Create page title in all other languages with cms.api.create_title()
        """
        for language_code, lang_name in iter_languages(self.languages):
            try:
                title = Title.objects.get(page=page, language=language_code)
            except Title.DoesNotExist:
                slug = self.get_slug(language_code, lang_name)
                assert slug != "", "No slug for %r" % language_code
                title = create_title(
                    language=language_code,
                    title=self.get_title(language_code, lang_name),
                    page=page,
                    slug = slug,
                )
                log.debug("Title created: %s", title)
            else:
                log.debug("Page title exist: %s", title)

    def get_dummy_text(self, page, no, placeholder, language_code, lang_name):
        if no==1:
            source = self.prefix_dummy_part
        elif no==self.dummy_text_count:
            source = self.suffix_dummy_part
        else:
            source = self.dummy_text_part

        dummy_text = source.format(
            absolute_url = page.get_absolute_url(language=language_code),
            no = no,
            slot = placeholder.slot,
            language_code = language_code,
            lang_name = lang_name,
        )
        return dummy_text

    def get_add_plugin_kwargs(self, page, no, placeholder, language_code, lang_name):
        """
        Return "content" for create the plugin.
        Called from self.add_plugins()
        """
        return {
            "plugin_type": 'TextPlugin', # djangocms_text_ckeditor
            "body": self.get_dummy_text(page, no, placeholder, language_code, lang_name)
        }

    def add_plugins(self, page, placeholder):
        """
        Add a "TextPlugin" in all languages.
        """
        for language_code, lang_name in iter_languages(self.languages):
            for no in range(1, self.dummy_text_count+1):
                add_plugin_kwargs = self.get_add_plugin_kwargs(
                    page, no, placeholder, language_code, lang_name
                )

                log.info(
                    'add plugin to placeholder "%s" (pk:%i) in: %s - no: %i',
                    placeholder, placeholder.pk, lang_name, no
                )
                plugin = add_plugin(
                    placeholder=placeholder,
                    language=language_code,
                    **add_plugin_kwargs
                )
                log.info('Plugin "%s" (pk:%r) added.', str(plugin), plugin.pk)
                placeholder.save()

    def get_or_create_placeholder(self, page, placeholder_slot):
        """
        Add a placeholder if not exists.
        """
        placeholder, created = get_or_create_placeholder(
            page, placeholder_slot, delete_existing=self.delete_first
        )
        return placeholder, created

    def fill_content(self, page, placeholder_slot):
        """
        Add a placeholder to the page.
        Here we add a "TextPlugin" in all languages.
        """
        if len(placeholder_slot)==1:
            raise RuntimeError(placeholder_slot)
        placeholder, created = self.get_or_create_placeholder(page, placeholder_slot)
        self.add_plugins(page, placeholder)

    def create(self):
        page, created = self.create_page() # Create page (and page title) in default language
        self.create_title(page) # Create page title in all other languages
        if created:
            # Add plugins only on new created pages
            # otherwise we will add more and more plugins
            # on every run!
            for placeholder_slot in self.placeholder_slots:
                self.fill_content(page, placeholder_slot) # Add content to the created page.
        self.publish(page) # Publish page in all languages

        # Force to reload the url configuration.
        # Important for unittests to "find" all plugins ;)
        apphook_reload.reload_urlconf()

        return page, created


@pytest.fixture(scope="class")
def create_cms_index_pages(placeholder_slot="content"):
    """
    create cms home page and fill >content< placeholder with TextPlugin
    """
    try:
        index_page = Page.objects.get(is_home=True, publisher_is_draft=False)
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
                log.info('create %r', title)
                if language_code != settings.LANGUAGE_CODE:
                    create_title(language_code, title, index_page)
                add_plugin(
                    placeholder=placeholder,
                    plugin_type='TextPlugin', # djangocms_text_ckeditor
                    language=language_code,
                    body='index page in %s' % lang_name
                )
                index_page.publish(language_code)
        created = True
    else:
        created = False
        log.debug('Index page already exists.')

    return index_page, created


class CmsPluginPageCreator(CmsPageCreator):
    """
    Create a Django CMS plugin page and fill the content.
    Useable for default production fixtures or unittests fixtures.

    The idea is to inherit from this class and update it for your need by
    overwrite some methods ;)
    """
    placeholder_slots=() # Fill no placeholders

    def __init__(self, apphook, apphook_namespace, *args, **kwargs):
        self.apphook = apphook
        self.apphook_namespace = apphook_namespace

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

    def create(self):
        """
        Create the plugin page in all languages and fill dummy content.
        """
        plugin = CMSPlugin.objects.filter(plugin_type=self.apphook)
        if plugin.exists():
            log.debug('Plugin page for "%s" plugin already exist, ok.', self.apphook)
            raise plugin

        page, created = super(CmsPluginPageCreator, self).create()

        if created:
            # Add a plugin with content in all languages to the created page.
            # But only on new created page
            for placeholder_slot in self.placeholder_slots:
                self.fill_content(page, placeholder_slot)

        return page, created


def create_cms_plugin_page(apphook, apphook_namespace, placeholder_slot=None):
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
    )
    creator.placeholder_slot=placeholder_slot
    plugin_page = creator.create()
    return plugin_page



class DummyPageGenerator(CmsPageCreator):
    def __init__(self, delete_first=False, title_prefix=None, levels=3, count=2):
        if title_prefix is None:
            self.title_prefix = self.__class__.__name__
        else:
            self.title_prefix = title_prefix

        self.levels = levels
        self.current_level = 1
        self.count = count
        self.current_count = 1
        self.page_data = {}
        super(DummyPageGenerator, self).__init__(delete_first=delete_first)

    def get_title(self, language_code, lang_name):
        """
        :return: 'title' string for cms.api.create_page()
        """
        title = "%s %i-%i in %s" % (
            self.title_prefix,
            self.current_count, self.current_level,
            language_code
        )
        log.info(title)
        return title

    def get_parent_page(self):
        """
        For 'parent' in cms.api.create_page()
        """
        if self.current_level == 1:
            # 'root' page
            return None
        else:
            return self.page_data[(self.current_level-1, self.current_count)]

    def create(self):
        for count in range(1, self.count+1):
            self.current_count = count
            for level in range(1, self.levels+1):
                self.current_level = level

                log.info("Level: %i current count: %i" % (self.current_level, self.current_count))

                page, created = super().create() # Create page (and page title) in default language
                self.page_data[(self.current_level, self.current_count)] = page

        # Force to reload the url configuration.
        # Important for unittests to "find" all plugins ;)
        apphook_reload.reload_urlconf()

        return self.page_data


def create_dummy_pages(delete_first, title_prefix, levels, count):
    page_data = DummyPageGenerator(
        delete_first=delete_first,
        title_prefix=title_prefix,
        levels=levels,
        count=count
    ).create()
    return page_data
