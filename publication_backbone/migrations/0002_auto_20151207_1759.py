# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publication_backbone', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publication',
            name='description',
        ),
        migrations.AddField(
            model_name='publication',
            name='comments_enabled',
            field=models.BooleanField(default=True, verbose_name='Comments enabled'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='publication',
            name='is_main',
            field=models.BooleanField(default=False, verbose_name='Main material'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='publication',
            name='lead',
            field=models.TextField(null=True, verbose_name='lead', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='publication',
            name='show_date',
            field=models.BooleanField(default=True, help_text='Show date', verbose_name='Show date'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='publication',
            name='sub_name',
            field=models.CharField(max_length=255, null=True, verbose_name='Sub name', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='publication',
            name='tags',
            field=models.CharField(help_text='use semicolon as tag divider', max_length=255, verbose_name='tags', blank=True),
            preserve_default=True,
        ),
    ]
