# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publication_backbone', '0005_publication_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staticplaceholder',
            name='site',
            field=models.ForeignKey(verbose_name='site', to='sites.Site'),
            preserve_default=True,
        ),
    ]
