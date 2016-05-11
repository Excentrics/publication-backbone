# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import publication_backbone.utils.media


class Migration(migrations.Migration):

    dependencies = [
        ('picture', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pictureitem',
            name='image',
            field=models.ImageField(upload_to=publication_backbone.utils.media.get_media_path, verbose_name='Image'),
            preserve_default=True,
        ),
    ]
