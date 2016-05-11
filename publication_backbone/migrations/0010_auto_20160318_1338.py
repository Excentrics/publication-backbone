# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('publication_backbone', '0009_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='rubrics',
            field=mptt.fields.TreeManyToManyField(related_name='catalog_items', verbose_name='rubrics', to='publication_backbone.Rubric', blank=True),
            preserve_default=True,
        ),
    ]
