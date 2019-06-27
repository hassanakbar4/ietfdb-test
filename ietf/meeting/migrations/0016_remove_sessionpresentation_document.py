# Copyright The IETF Trust 2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-21 03:57


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0018_remove_old_document_field'),
        ('meeting', '0015_sessionpresentation_document2_fk'),
    ]

    operations = [

        # We need to get rid of the current through table uniqueness
        # constraint before we can remove the document column: The table
        # has "UNIQUE KEY `session_id` (`session_id`,`document_id`)"
        migrations.RunSQL(
            "ALTER TABLE `meeting_session_materials` DROP INDEX `session_id`;",
            "CREATE UNIQUE INDEX `session_id` ON `meeting_session_materials` (`session_id`, `document_id`);"
        ),
        ## This doesn't work:
        # migrations.RemoveIndex(
        #     model_name='sessionpresentation',
        #     name='session_id'
        # ),
        migrations.RemoveField(
            model_name='sessionpresentation',
            name='document',
        ),
    ]
