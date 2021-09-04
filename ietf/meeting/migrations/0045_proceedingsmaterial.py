# Copyright The IETF Trust 2021 All Rights Reserved

# Generated by Django 2.2.24 on 2021-07-26 17:09

from django.db import migrations, models
import django.db.models.deletion
import ietf.utils.models


class Migration(migrations.Migration):

    dependencies = [
        ('name', '0029_proceedingsmaterialtypename'),
        ('meeting', '0044_again_assign_correct_constraintnames'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProceedingsMaterial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meeting', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proceedings_materials', to='meeting.Meeting')),
                ('type', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='name.ProceedingsMaterialTypeName')),
                ('document', ietf.utils.models.ForeignKey(limit_choices_to={'type_id': 'procmaterials'}, on_delete=django.db.models.deletion.CASCADE, to='doc.Document', unique=True)),
            ],
            options={
                'unique_together': {('meeting', 'type')},
            },
        ),
    ]
