# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-08 16:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0016_auto_20160608_1535'),
        ('plugin_anchor_menu', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DropDownAnchorMenuPluginModel',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='plugin_anchor_menu_dropdownanchormenupluginmodel', serialize=False, to='cms.CMSPlugin')),
                ('menu_id', models.SlugField(default='anchor_menu', max_length=254, verbose_name='The internal menu ID')),
                ('link_type', models.CharField(choices=[('h', "Add '#anchor' to browser addess."), ('s', "Don't add '#anchor' to browser addess.")], default='s', max_length=1, verbose_name='Link type')),
                ('first_label', models.CharField(blank=True, default='Please select', help_text='Label for the first option. (The first anchor will be used, if empty)', max_length=254, null=True, verbose_name='First label')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
