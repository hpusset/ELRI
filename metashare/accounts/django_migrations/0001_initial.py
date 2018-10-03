# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.exceptions
from django.conf import settings
import metashare.accounts.validators
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessPointEdeliveryApplication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('endpoint', models.URLField(max_length=150, verbose_name=b'MSH Endpoint', validators=[metashare.accounts.validators.validate_wsdl_url])),
                ('gateway_party_name', models.CharField(max_length=100, verbose_name=b'Gateway Party Name')),
                ('gateway_party_id', models.CharField(max_length=100, verbose_name=b'Gateway Party ID')),
                ('public_key', models.FileField(upload_to=b'/path/to/app/certs/dir', verbose_name=b'Public Cetificate')),
                ('status', models.CharField(max_length=10, verbose_name=b'Application Status', choices=[(b'PENDING', b'PENDING'), (b'REJECTED', b'REJECTED'), (b'ACTIVE', b'ACTIVE'), (b'REVOKED', b'REVOKED')])),
                ('rejection_reason', models.TextField(max_length=1000, null=True, verbose_name=b'Rejection Reason', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name=b'Date Created')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EditorGroup',
            fields=[
                ('group_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='auth.Group')),
            ],
            options={
            },
            bases=('auth.group',),
        ),
        migrations.CreateModel(
            name='EditorGroupApplication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('editor_group', models.OneToOneField(to='accounts.EditorGroup')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EditorGroupManagers',
            fields=[
                ('group_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='auth.Group')),
                ('managed_group', models.OneToOneField(to='accounts.EditorGroup')),
            ],
            options={
                'verbose_name': 'editor group managers group',
            },
            bases=('auth.group',),
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('group_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='auth.Group')),
            ],
            options={
            },
            bases=('auth.group',),
        ),
        migrations.CreateModel(
            name='OrganizationApplication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('organization', models.OneToOneField(to='accounts.Organization')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrganizationManagers',
            fields=[
                ('group_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='auth.Group')),
                ('managed_organization', models.OneToOneField(to='accounts.Organization')),
            ],
            options={
                'verbose_name': 'organization managers group',
            },
            bases=('auth.group',),
        ),
        migrations.CreateModel(
            name='RegistrationRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(max_length=32, null=True, verbose_name=b'UUID', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResetRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(max_length=32, null=True, verbose_name=b'UUID', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('uuid', models.CharField(max_length=32, null=True, verbose_name=b'UUID', blank=True)),
                ('birthdate', models.DateField(null=True, verbose_name=b'Date of birth', blank=True)),
                ('phone_number', models.CharField(blank=True, max_length=50, null=True, verbose_name=b'Phone Number', validators=[django.core.validators.RegexValidator(b'^\\+(?:[0-9] ?){6,14}[0-9]$', b'Not a valid phone number', django.core.exceptions.ValidationError)])),
                ('country', models.CharField(blank=True, max_length=100, null=True, verbose_name=b'Country', choices=[(b'Austria', b'Austria'), (b'Belgium', b'Belgium'), (b'Bulgaria', b'Bulgaria'), (b'Croatia', b'Croatia'), (b'Cyprus', b'Cyprus'), (b'Czech Republic', b'Czech Republic'), (b'Denmark', b'Denmark'), (b'Estonia', b'Estonia'), (b'Finland', b'Finland'), (b'France', b'France'), (b'Germany', b'Germany'), (b'Greece', b'Greece'), (b'Hungary', b'Hungary'), (b'Iceland', b'Iceland'), (b'Ireland', b'Ireland'), (b'Italy', b'Italy'), (b'Latvia', b'Latvia'), (b'Lithuania', b'Lithuania'), (b'Luxembourg', b'Luxembourg'), (b'Malta', b'Malta'), (b'Netherlands', b'Netherlands'), (b'Norway', b'Norway'), (b'Poland', b'Poland'), (b'Portugal', b'Portugal'), (b'Romania', b'Romania'), (b'Slovakia', b'Slovakia'), (b'Slovenia', b'Slovenia'), (b'Spain', b'Spain'), (b'Sweden', b'Sweden'), (b'United Kingdom', b'United Kingdom')])),
                ('affiliation', models.TextField(verbose_name=b'Affiliation(s)', blank=True)),
                ('position', models.CharField(max_length=50, blank=True)),
                ('homepage', models.URLField(blank=True)),
                ('default_editor_groups', models.ManyToManyField(to='accounts.EditorGroup', blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('ms_associate_member', 'Is a META-SHARE associate member.'), ('ms_full_member', 'Is a META-SHARE full member.')),
            },
            bases=(models.Model,),
        ),
    ]
