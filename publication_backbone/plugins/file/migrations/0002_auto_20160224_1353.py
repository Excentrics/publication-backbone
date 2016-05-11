# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('file', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileitem',
            name='template',
            field=models.CharField(default=(b'publication_backbone/plugins/file/default.html', 'Default file'), max_length=255, verbose_name='Template', choices=[(b'publication_backbone/plugins/file/default.html', 'Default file'), (b'publication_backbone/plugins/file/hidden.html', 'Hidden file')]),
            preserve_default=True,
        ),
    ]
