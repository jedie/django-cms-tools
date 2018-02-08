
import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin

log = logging.getLogger(__name__)


class AnchorPluginModel(CMSPlugin):
    title=models.CharField(_("Title"), max_length=254)
    slug=models.SlugField(verbose_name=_("Slug"), max_length=255)

    def __str__(self):
        return self.title
