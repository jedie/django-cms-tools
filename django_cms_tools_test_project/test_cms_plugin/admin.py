from django.contrib import admin

# Django CMS Tools
from django_cms_tools_test_project.test_cms_plugin.models import EntryModel, ImageModel, RelatedPluginModel


@admin.register(RelatedPluginModel)
class RelatedPluginModelAdmin(admin.ModelAdmin):
    pass


@admin.register(EntryModel)
class EntryModelAdmin(admin.ModelAdmin):
    pass


@admin.register(ImageModel)
class ImageModelAdmin(admin.ModelAdmin):
    pass
