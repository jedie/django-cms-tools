# coding: utf-8

from __future__ import absolute_import, print_function, unicode_literals


from django.conf.urls import include, url, static
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin

from django_cms_tools_test_project import settings
from django_cms_tools_test_project.test_app.views import IndexView


admin.autodiscover()


urlpatterns = i18n_patterns(
    url(r'^admin/', include(admin.site.urls)),
    url(r'^index/', IndexView.as_view()),
    url(r'^', include('cms.urls')),
)

if settings.DEBUG:
    urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
