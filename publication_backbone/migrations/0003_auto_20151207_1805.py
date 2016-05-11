# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publication_backbone', '0002_auto_20151207_1759'),
    ]

    operations = [
        migrations.RenameField(
            model_name='publication',
            old_name='lead',
            new_name='description',
        ),
    ]
