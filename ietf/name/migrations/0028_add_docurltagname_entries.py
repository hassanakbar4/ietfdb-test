# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-09-27 10:29
from __future__ import unicode_literals

from django.db import migrations

def forwards(apps,schema_editor):
    DocUrlTagName = apps.get_model('name','DocUrlTagName')

    DocUrlTagName.objects.create(
        slug='wiki',
        name='Document wiki',
    )
    DocUrlTagName.objects.create(
        slug='issues',
        name='Document Issue Tracker',
    )
    DocUrlTagName.objects.create(
        slug='repository',
        name='Document Source Repository',
    )
    DocUrlTagName.objects.create(
        slug='yang-module',
        name='Extracted Yang Module',
    )
    DocUrlTagName.objects.create(
        slug='yang-impact-analysis',
        name='Yang Impact Analysis',
    )
    DocUrlTagName.objects.create(
        slug='yang-module-metadata',
        name='Yang module metadata',
    )

def backwards(apps,schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('name', '0027_docurltagname'),
        ('doc', '0034_documenturl'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
