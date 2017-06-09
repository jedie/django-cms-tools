# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function


from django.conf.urls import url

from django_cms_tools_test_project.test_cms_plugin.views import TestAppView

urlpatterns = [
    url(r'^$', TestAppView.as_view(), name='test_cms_app'),
]
