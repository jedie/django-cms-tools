# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_cms_tools.models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0016_auto_20160608_1535'),
    ]

    operations = [
        migrations.CreateModel(
            name='EntryModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('text', models.TextField(max_length=1023, verbose_name='Text')),
            ],
        ),
        migrations.CreateModel(
            name='RelatedPluginModel',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(related_name='test_cms_plugin_relatedpluginmodel', to='cms.CMSPlugin', parent_link=True, primary_key=True, serialize=False, auto_created=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(django_cms_tools.models.RelatedPluginModelMixin, 'cms.cmsplugin'),
        ),
        migrations.AddField(
            model_name='entrymodel',
            name='plugin',
            field=models.ForeignKey(to='test_cms_plugin.RelatedPluginModel', related_name='entries'),
        ),
    ]
