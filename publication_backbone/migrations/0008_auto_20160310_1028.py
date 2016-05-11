# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publication_backbone', '0007_auto_20160302_2201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='sub_name',
            field=models.CharField(max_length=600, null=True, verbose_name='sub name', blank=True),
            preserve_default=True,
        ),
    ]
