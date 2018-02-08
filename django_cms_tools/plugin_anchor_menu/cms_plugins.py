

import logging

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

# Django CMS Tools
from django_cms_tools.plugin_anchor_menu import constants as plugin_anchor_menu_constants
from django_cms_tools.plugin_anchor_menu import app_settings
from django_cms_tools.plugin_anchor_menu.models import AnchorPluginModel

log = logging.getLogger(__name__)


@plugin_pool.register_plugin
class AnchorPlugin(CMSPluginBase):
    """
    One anchor in a CMS page
    """
    name = _("Anchor")
    model = AnchorPluginModel
    render_template = app_settings.ANCHOR_MENU_TEMPLATE_ANCHOR
    cache = False
    prepopulated_fields = {"slug": ("title",)}


assert AnchorPlugin.__name__ == plugin_anchor_menu_constants.ANCHOR_PLUGIN_NAME


@plugin_pool.register_plugin
class DropDownAnchorMenuPlugin(CMSPluginBase):
    """
    Render a anchor menu
    """
    name = _("Drop-Down Anchor Menu")
    render_template = app_settings.ANCHOR_MENU_TEMPLATE_MENU
    cache = False

    def render(self, context, instance, placeholder):
        anchors = AnchorPluginModel.objects.all().filter(
            placeholder=instance.placeholder,
            language=instance.language,
        )
        context["anchors"] = anchors
        context["ANCHOR_MENU_ID"] = app_settings.ANCHOR_MENU_ID
        context["ANCHOR_MENU_JQUERY_URL"] = app_settings.ANCHOR_MENU_JQUERY_URL
        context["ANCHOR_MENU_SCROLL"] = app_settings.ANCHOR_MENU_SCROLL
        context["DEBUG"] = settings.DEBUG
        return super().render(context, instance, placeholder)


assert DropDownAnchorMenuPlugin.__name__ == plugin_anchor_menu_constants.DROP_DOWN_ANCHOR_MENU_PLUGIN_NAME
