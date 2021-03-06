# Copyright The IETF Trust 2020, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-21 14:27


from __future__ import absolute_import, print_function, unicode_literals

import re

from django.conf import settings
from django.db import migrations


def forward(apps, schema_editor):

    Document                     = apps.get_model('doc', 'Document')

    print('')
    for d in Document.objects.filter(external_url__contains="/b'"):
        match = re.search("^(%s/arch/msg/[^/]+/)b'([^']+)'$" % settings.MAILING_LIST_ARCHIVE_URL, d.external_url)
        if match:
            d.external_url = "%s%s" % (match.group(1), match.group(2))
            d.save()
            print('Fixed url #%s: %s' % (d.id, d.external_url))

def reverse(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0029_add_ipr_event_types'),
    ]

    operations = [
        migrations.RunPython(forward, reverse),
    ]
