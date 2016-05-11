# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interview', '0005_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='interviewquestion',
            name='is_right',
            field=models.BooleanField(default=False, verbose_name='Right answer'),
            preserve_default=True,
        ),
    ]
