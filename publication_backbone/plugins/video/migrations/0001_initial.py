# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_contents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoItem',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem')),
                ('video_url', models.CharField(help_text='For example: http://www.youtube.com/watch?v=0PJBSRAzQKs', max_length=255, verbose_name='Youtube video code')),
                ('width', models.PositiveIntegerField(default=560, verbose_name='Video width')),
                ('height', models.PositiveIntegerField(default=315, verbose_name='Video height')),
                ('title', models.CharField(max_length=255, verbose_name='title', blank=True)),
                ('author', models.CharField(max_length=255, verbose_name='author', blank=True)),
            ],
            options={
                'db_table': 'contentitem_video_videoitem',
                'verbose_name': 'Video',
                'verbose_name_plural': 'Videos',
            },
            bases=('fluent_contents.contentitem',),
        ),
    ]
