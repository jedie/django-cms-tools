import logging

from cms.api import add_plugin
from django.conf import settings
from django.utils.text import slugify

from django_cms_tools.fixtures.pages import CmsPageCreator
from django_cms_tools.plugin_anchor_menu import constants as plugin_anchor_menu_constants


log = logging.getLogger(__name__)


class AnchorTestPageCreator(CmsPageCreator):
    placeholder_slots = ("content",)
    dummy_text_count = 1

    def get_add_plugin_kwargs(self, page, no, placeholder, language_code, lang_name):
        """
        Return "content" for create the plugin.
        Called from self.add_plugins()
        """
        assert placeholder.slot == "content"

        log.info("Add drop-down menu plugin %s for %s...", lang_name, placeholder)
        add_plugin(
            placeholder=placeholder,
            plugin_type=plugin_anchor_menu_constants.DROP_DOWN_ANCHOR_MENU_PLUGIN_NAME,
            language=language_code,
        )

        for i in range(10):
            title="dummy text no. %i" % i
            slug=slugify(title)
            # log.debug("Create ancor %r with slug %s", title, slug)
            add_plugin(
                placeholder=placeholder,
                plugin_type=plugin_anchor_menu_constants.ANCHOR_PLUGIN_NAME,
                language=language_code,
                title=title,
                slug=slug,
            )
            add_plugin(
                placeholder=placeholder,
                plugin_type=settings.CKEDITOR,
                language=language_code,
                body=self.get_dummy_text(page, i, placeholder, language_code, lang_name),
            )

        return {
            "plugin_type": "TextPlugin",
            "body": "<p><strong>page end</strong></p>"
        }



# called from django_cms_tools_test_project.test_app.management.commands.run_test_project_dev_server.Command#handle
def create_anchor_test_page(delete_first=False):
    AnchorTestPageCreator(delete_first=delete_first).create()
