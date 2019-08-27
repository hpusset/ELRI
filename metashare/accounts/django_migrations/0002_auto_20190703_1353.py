# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='homepage',
            field=models.URLField(verbose_name='Homepage', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='position',
            field=models.CharField(max_length=50, verbose_name='Position', blank=True),
            preserve_default=True,
        ),
    ]
