# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class TestAppConfig(AppConfig):

    name = 'test_project.test_cms_app'
    verbose_name = _('Simple Test App')
