
from django.utils.translation import ugettext_lazy as _
from django.apps import AppConfig


class LandingPageConfig(AppConfig):
    # Full Python path to the application:
    name = 'django_cms_tools.plugin_landing_page'

    # Human-readable name for the application:
    verbose_name = _("Landing Page")
