# Copyright The IETF Trust 2020, All Rights Reserved

from urllib.parse import urlparse
from django.db import migrations

def categorize(url):
    # This will categorize a few urls pointing into files in a repo as a repo, but that's better than calling them an org
    element_count = len(urlparse(url).path.strip('/').split('/'))
    if element_count < 1:
        print("Bad github resource:",url)
    return 'github_org' if element_count == 1 else 'github_repo' 

def forward(apps, schema_editor):
    DocExtResource = apps.get_model('doc','DocExtResource')

    for resource in DocExtResource.objects.filter(name__slug__in=('github_org','github_repo')):
        category = categorize(resource.value)
        if resource.name_id != category:
            resource.name_id = category
            resource.save()

def reverse(apps, schema_editor):
    # Intentionally don't try to return to former worse state
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0035_populate_docextresources'),
    ]

    operations = [
        migrations.RunPython(forward, reverse),
    ]
