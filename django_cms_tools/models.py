

class RelatedPluginModelMixin:
    """
    http://docs.django-cms.org/en/latest/how_to/custom_plugins.html#for-foreign-key-relations-from-other-objects

    Related model must look like this:

        class EntryModel(models.Model):
            plugin = models.ForeignKey(<CMSPluginModel>, related_name="entries")

    Important:
        - ForeignKey attribute must be named: 'plugin'
        - 'related_name' == "entries"
    """
    def copy_relations(self, oldinstance):
        # Before copying related objects from the old instance, the ones
        # on the current one need to be deleted. Otherwise, duplicates may
        # appear on the public version of the page
        self.entries.all().delete()

        for associated_item in oldinstance.entries.all():
            # instance.pk = None; instance.pk.save() is the slightly odd but
            # standard Django way of copying a saved model instance
            associated_item.pk = None
            associated_item.plugin = self
            associated_item.save()
