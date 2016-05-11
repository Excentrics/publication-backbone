# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interview', '0008_auto_20160331_1815'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='failure_text',
            field=models.CharField(default=b'', help_text='Failure result text', max_length=255, verbose_name='Failure text'),
            preserve_default=True,
        ),
    ]
