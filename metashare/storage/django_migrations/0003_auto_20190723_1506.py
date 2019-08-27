# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0002_auto_20190703_1353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storageobject',
            name='publication_status',
            field=models.CharField(default=b'i', help_text='Generalized publication status flag for this storage object instance.', max_length=1, choices=[(b'i', b'internal'), (b'g', b'ingested'), (b'r', b'processing'), (b'e', b'error'), (b'p', b'published')]),
            preserve_default=True,
        ),
    ]
