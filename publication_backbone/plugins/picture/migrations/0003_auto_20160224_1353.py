# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('picture', '0002_auto_20151221_1600'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pictureitem',
            name='template',
            field=models.CharField(default=(b'publication_backbone/plugins/picture/default.html', 'Thumbnail picture / Gallery'), max_length=255, verbose_name='Template', choices=[(b'publication_backbone/plugins/picture/default.html', 'Thumbnail picture / Gallery'), (b'publication_backbone/plugins/picture/slider.html', 'Simple picture / Slider')]),
            preserve_default=True,
        ),
    ]
