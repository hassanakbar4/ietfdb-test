# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-04-15 10:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import ietf.utils.models


class Migration(migrations.Migration):

    dependencies = [
        ('name', '0010_extres'),
        ('doc', '0031_set_state_for_charters_of_replaced_groups'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocExtResource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_name', models.CharField(blank=True, default='', max_length=255)),
                ('value', models.CharField(max_length=2083)),
                ('doc', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doc.Document')),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='name.ExtResourceName')),
            ],
        ),
    ]
