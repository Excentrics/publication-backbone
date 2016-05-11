# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publication_backbone', '0006_auto_20160224_1345'),
        ('promo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='promopluginmodel',
            name='to_publication',
            field=models.ForeignKey(related_name='promo_backward_relations', verbose_name='to publication', to='publication_backbone.Publication', null=True),
            preserve_default=True,
        ),
    ]
