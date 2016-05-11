# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publication_backbone', '0004_auto_20160118_1710'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='author',
            field=models.CharField(max_length=255, null=True, verbose_name='author', blank=True),
            preserve_default=True,
        ),
    ]
