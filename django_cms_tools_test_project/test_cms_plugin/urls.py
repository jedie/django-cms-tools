from django.conf.urls import url

# Django CMS Tools
from django_cms_tools_test_project.test_cms_plugin.views import TestAppView

urlpatterns = [
    url(r'^$', TestAppView.as_view(), name='test_cms_app'),
]
