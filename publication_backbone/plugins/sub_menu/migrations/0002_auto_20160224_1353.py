# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sub_menu', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submenu',
            name='template',
            field=models.CharField(default=(b'publication_backbone/plugins/sub_menu/default.html', 'Default sub menu'), max_length=255, verbose_name='Template', choices=[(b'publication_backbone/plugins/sub_menu/default.html', 'Default sub menu'), (b'publication_backbone/plugins/sub_menu/horizontal.html', 'As string submenu')]),
            preserve_default=True,
        ),
    ]
