# Copyright The IETF Trust 2020, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-03-19 11:42
from __future__ import unicode_literals

from collections import namedtuple

from django.db import migrations


def forward(apps, schema_editor):
    ExtResourceName = apps.get_model('name','ExtResourceName')
    ExtResourceTypeName = apps.get_model('name','ExtResourceTypeName')

    ExtResourceTypeName.objects.create(slug='email', name="Email address", desc="Email address", used=True, order=0)
    ExtResourceTypeName.objects.create(slug='url', name="URL", desc="URL", used=True, order=0)
    ExtResourceTypeName.objects.create(slug='string', name="string", desc="string", used=True, order=0)

    resourcename = namedtuple('resourcename', ['slug', 'name', 'type'])
    resourcenames= [
        resourcename("webpage", "Additional Web Page", "url"),
        resourcename("faq", "Frequently Asked Questions", "url"),
        resourcename("github_username","GitHub Username", "string"),
        resourcename("github_org","GitHub Organization", "url"),
        resourcename("github_repo","GitHub Repository", "url"),
        resourcename("gitlab_username","GitLab Username", "string"),
        resourcename("tracker","Issuer Tracker", "url"),
        resourcename("slack","Slack Channel", "url"),
        resourcename("wiki","Wiki", "url"),
        resourcename("yc_entry","Yang Catalog Entry", "url"),
        resourcename("yc_impact","Yang Impact Analysis", "url"),
        resourcename("jabber_room","Jabber Room", "url"),
        resourcename("jabber_log","Jabber Log", "url"),
        resourcename("mailing_list","Mailing List", "url"),
        resourcename("mailing_list_archive","Mailing List Archive","url"),
        resourcename("repo","Other Repository", "url")
    ]

    for name in resourcenames:
        ExtResourceName.objects.create(slug=name.slug, name=name.name, desc=name.name, used=True, order=0, type_id=name.type)



def reverse(apps, schema_editor):
    ExtResourceName = apps.get_model('name','ExtResourceName')
    ExtResourceTypeName = apps.get_model('name','ExtResourceTypeName')

    ExtResourceName.objects.all().delete()
    ExtResourceTypeName.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('name', '0014_extres'),
        ('group', '0033_extres'),
        ('doc', '0034_extres'),
        ('person', '0015_extres'),
        # this is only for the purpose of grouping schema migrations together
        # in a release, not because there's an actual dependency:
        ('meeting', '0030_allow_empty_joint_with_sessions'), 
    ]

    operations = [
        migrations.RunPython(forward, reverse)
    ]
