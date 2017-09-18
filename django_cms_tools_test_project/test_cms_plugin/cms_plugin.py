
"""
    created 18.09.2017 by Jens Diemer
"""


from django.contrib import admin

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from django_cms_tools_test_project.test_cms_plugin.models import EntryModel, RelatedPluginModel


class EntryInlineAdmin(admin.TabularInline):
    model = EntryModel


class RelatedPlugin(CMSPluginBase):
    model = RelatedPluginModel
    name = "Related Plugin"
    module = "Django CMS Tools Test"
    render_template = "related_cms_plugin.html"
    cache = False
    inlines = (EntryInlineAdmin,)


plugin_pool.register_plugin(RelatedPlugin)
