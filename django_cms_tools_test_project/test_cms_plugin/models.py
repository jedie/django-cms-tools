# coding: utf-8

"""
    created 18.09.2017 by Jens Diemer
"""

from __future__ import absolute_import, print_function, unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models.pluginmodel import CMSPlugin

# Django CMS Tools
from django_cms_tools.models import RelatedPluginModelMixin


class RelatedPluginModel(RelatedPluginModelMixin, CMSPlugin):
    pass


class EntryModel(models.Model):
    """
    One entry for RelatedPluginModel
    """
    plugin = models.ForeignKey(RelatedPluginModel, related_name="entries")
    text = models.TextField(_("Text"), max_length=1023)
