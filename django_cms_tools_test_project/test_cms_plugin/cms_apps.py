# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function


from cms.apphook_pool import apphook_pool
from cms.app_base import CMSApp

from django_cms_tools_test_project.test_cms_plugin.app_config import TestAppConfig
from django_cms_tools_test_project.test_cms_plugin import urls

class SimpleTestApp(CMSApp):

    app_name = 'simpletest'
    name = TestAppConfig.verbose_name

    def get_urls(self, page=None, language=None, **kwargs):
        return [urls.__name__] # test_project.test_cms_plugin.urls

    # def get_menus(self, page=None, language=None, **kwargs):
    #     from test_project.test_cms_app.cms_menus import TestMenu
    #     return [TestMenu]


apphook_pool.register(SimpleTestApp)
