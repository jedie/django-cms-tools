import posixpath

from django.conf import settings


# Used templates:
ANCHOR_MENU_TEMPLATE_ANCHOR = getattr(settings, "ANCHOR_MENU_TEMPLATE_ANCHOR", "anchor_menu/anchor.html")
ANCHOR_MENU_TEMPLATE_MENU = getattr(settings, "ANCHOR_MENU_TEMPLATE_MENU", "anchor_menu/menu.html")


# just use django's jquery version as default:
# set ANCHOR_MENU_JQUERY_URL=None if no jquery should be loaded!
ANCHOR_MENU_JQUERY_URL = getattr(settings, "ANCHOR_MENU_JQUERY_URL",
    posixpath.join(settings.STATIC_URL, "admin/js/vendor/jquery/jquery.min.js")
)


# The id for <select> in templates/anchor_menu/menu.html
ANCHOR_MENU_DEFAULT_ID = getattr(settings, "ANCHOR_MENU_DEFAULT_ID", "anchor_menu")


# If =="s": scroll with jQuery: The #anchor will not added to url
# If =="h": scroll by window.location.href so the #anchor will added to url
ANCHOR_MENU_DEFAULT_TYPE = getattr(settings, "ANCHOR_MENU_DEFAULT_TYPE", "s")
