# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storageobject',
            name='legacy_resource',
            field=models.BooleanField(default=False, help_text='Specifies whether the resource is collected by ELRI 1'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='storageobject',
            name='publication_status',
            field=models.CharField(default=b'i', help_text='Generalized publication status flag for this storage object instance.', max_length=1, choices=[(b'i', b'internal'), (b'g', b'ingested'), (b'r', b'processing'), (b'e', b'error'), (b'p', b'published'), (b'c', b'published and ELRC uploaded')]),
            preserve_default=True,
        ),
    ]
