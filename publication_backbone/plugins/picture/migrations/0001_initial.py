# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import fluent_contents.extensions


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_contents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PictureItem',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem')),
                ('image', fluent_contents.extensions.PluginImageField(max_length=100, verbose_name='Image')),
                ('caption', models.CharField(max_length=255, verbose_name='Caption', blank=True)),
                ('author', models.CharField(max_length=255, verbose_name='Author', blank=True)),
                ('template', models.CharField(default=(b'publication_backbone/plugins/picture/default.html', 'Default picture'), max_length=255, verbose_name='Template', choices=[(b'publication_backbone/plugins/picture/default.html', 'Default picture'), (b'publication_backbone/plugins/picture/simple.html', 'Simple picture')])),
                ('url', fluent_contents.extensions.PluginUrlField(max_length=300, verbose_name='URL', blank=True)),
            ],
            options={
                'db_table': 'contentitem_picture_pictureitem',
                'verbose_name': 'Picture',
                'verbose_name_plural': 'Pictures',
            },
            bases=('fluent_contents.contentitem',),
        ),
    ]
