# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import metashare.storage.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StorageObject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source_url', models.URLField(default=b'http://127.0.0.1:8000', help_text='(Read-only) base URL for the server where the master copy of the associated language resource is located.', editable=False)),
                ('identifier', models.CharField(help_text='(Read-only) unique identifier for this storage object instance.', max_length=64, null=True, editable=False, blank=True)),
                ('created', models.DateTimeField(help_text='(Read-only) creation date for this storage object instance.', auto_now_add=True)),
                ('modified', models.DateTimeField(help_text='(Read-only) last modification date of the metadata XML for this storage object instance.', auto_now=True)),
                ('checksum', models.CharField(help_text='(Read-only) MD5 checksum of the binary data for this storage object instance.', max_length=32, null=True, blank=True)),
                ('digest_checksum', models.CharField(help_text='(Read-only) MD5 checksum of the digest zip file containing the global serialized storage object and the metadata XML for this storage object instance.', max_length=32, null=True, blank=True)),
                ('digest_modified', models.DateTimeField(help_text='(Read-only) last modification date of digest zip for this storage object instance.', null=True, editable=False, blank=True)),
                ('digest_last_checked', models.DateTimeField(help_text='(Read-only) last update check date of digest zip for this storage object instance.', null=True, editable=False, blank=True)),
                ('revision', models.PositiveIntegerField(default=1, help_text='Revision or version information for this storage object instance.')),
                ('metashare_version', models.CharField(default=b'3.1.1', help_text='(Read-only) META-SHARE version used with the storage object instance.', max_length=32, editable=False)),
                ('legacy_resource', models.BooleanField(default=False, help_text='Specifies whether the resource is collected by ELRC 1')),
                ('copy_status', models.CharField(default=b'm', help_text='Generalized copy status flag for this storage object instance.', max_length=1, editable=False, choices=[(b'm', b'master copy'), (b'r', b'remote copy'), (b'p', b'proxy copy')])),
                ('publication_status', models.CharField(default=b'i', help_text='Generalized publication status flag for this storage object instance.', max_length=1, choices=[(b'i', b'internal'), (b'g', b'ingested'), (b'p', b'published')])),
                ('source_node', models.CharField(help_text='(Read-only) id of source node from which the resource originally stems as set in local_settings.py in CORE_NODES and PROXIED_NODES; empty if resource stems from this local node', max_length=32, null=True, editable=False, blank=True)),
                ('deleted', models.BooleanField(default=False, help_text='Deletion status flag for this storage object instance.')),
                ('metadata', models.TextField(help_text='XML containing the metadata description for this storage object instance.', validators=[metashare.storage.models._validate_valid_xml])),
                ('global_storage', models.TextField(default=b'not set yet', help_text='text containing the JSON serialization of global attributes for this storage object instance.')),
                ('local_storage', models.TextField(default=b'not set yet', help_text='text containing the JSON serialization of local attributes for this storage object instance.')),
            ],
            options={
                'permissions': (('can_sync', 'Can synchronize'),),
            },
            bases=(models.Model,),
        ),
    ]
