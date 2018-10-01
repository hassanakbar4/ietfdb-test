# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-30 09:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0005_fix_replaced_iab_irtf_stream_docs'),
    ]

    operations = [
        migrations.CreateModel(
            name='BallotCommentDocEvent',
            fields=[
                ('docevent_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='doc.DocEvent')),
                ('send_email', models.BooleanField(default=False)),
            ],
            bases=('doc.docevent',),
        ),
    ]
