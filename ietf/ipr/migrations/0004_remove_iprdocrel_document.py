# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-20 09:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ipr', '0003_add_ipdocrel_document2_fk'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='iprdocrel',
            name='document',
        ),
    ]
