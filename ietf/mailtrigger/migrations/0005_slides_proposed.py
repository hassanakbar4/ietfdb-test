# Copyright The IETF Trust 2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-25 06:11


from django.db import migrations

def forward(apps, schema_editor):
    MailTrigger = apps.get_model('mailtrigger', 'MailTrigger')
    Recipient = apps.get_model('mailtrigger', 'Recipient')

    changed = MailTrigger.objects.create(
        slug = 'slides_proposed',
        desc = 'Recipients when slides are proposed for a given session',
    )
    changed.to.set(Recipient.objects.filter(slug__in=['group_chairs', 'group_responsible_directors', 'group_secretaries']))

def reverse(apps, schema_editor):
    MailTrigger = apps.get_model('mailtrigger','MailTrigger')
    MailTrigger.objects.filter(slug='slides_proposed').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('mailtrigger', '0004_ballot_rfceditornote_changed_postapproval'),
    ]

    operations = [
        migrations.RunPython(forward,reverse)
    ]
