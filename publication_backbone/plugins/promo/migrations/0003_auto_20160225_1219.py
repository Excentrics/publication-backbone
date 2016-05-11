# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('promo', '0002_promopluginmodel_to_publication'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promopluginmodel',
            name='to_publication',
            field=models.ForeignKey(related_name='promo_publication_relation', verbose_name='to publication', blank=True, to='publication_backbone.Publication', null=True),
            preserve_default=True,
        ),
    ]
