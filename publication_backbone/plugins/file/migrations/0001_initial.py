# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import publication_backbone.utils.media


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_contents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileItem',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem')),
                ('file', models.FileField(upload_to=publication_backbone.utils.media.get_media_path, verbose_name='File')),
                ('caption', models.CharField(max_length=255, verbose_name='Caption', blank=True)),
                ('template', models.CharField(default=(b'publication_backbone/plugins/file/default.html', 'Default file'), max_length=255, verbose_name='Template', choices=[(b'publication_backbone/plugins/file/default.html', 'Default file')])),
            ],
            options={
                'db_table': 'contentitem_file_fileitem',
                'verbose_name': 'File',
                'verbose_name_plural': 'Files',
            },
            bases=('fluent_contents.contentitem',),
        ),
    ]
