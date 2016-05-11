# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publication_backbone', '0006_auto_20160224_1345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='sub_name',
            field=models.CharField(max_length=500, null=True, verbose_name='sub name', blank=True),
            preserve_default=True,
        ),
    ]
