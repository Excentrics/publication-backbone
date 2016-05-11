# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('interview', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='interview',
            options={'ordering': ['date_added'], 'verbose_name': 'interview', 'verbose_name_plural': 'interviews'},
        ),
        migrations.AddField(
            model_name='interview',
            name='date_added',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='date added'),
            preserve_default=True,
        ),
    ]
