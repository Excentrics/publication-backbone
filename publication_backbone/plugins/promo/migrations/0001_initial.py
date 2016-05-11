# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('publication_backbone', '0006_auto_20160224_1345'),
        ('fluent_contents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PromoPluginModel',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem')),
                ('count', models.PositiveIntegerField(default=5, verbose_name='Display count')),
                ('order', models.CharField(default=b'date_added_asc', max_length=255, verbose_name='Display Order', blank=True, choices=[(b'date_added_asc', 'Date Added: old first'), (b'date_added_desc', 'Date Added: new first'), (b'name_desc', 'Alphabetical: descending'), (b'name_asc', 'Alphabetical')])),
                ('template', models.CharField(default=(b'publication_backbone/plugins/promo/promo_default.html', 'Default promo'), max_length=255, verbose_name='Template', choices=[(b'publication_backbone/plugins/promo/promo_default.html', 'Default promo'), (b'publication_backbone/plugins/promo/promo_list.html', 'List promo'), (b'publication_backbone/plugins/promo/promo.html', 'Top links promo'), (b'publication_backbone/plugins/promo/promo_bottom.html', 'Bottom links promo')])),
                ('categories', mptt.fields.TreeManyToManyField(related_name='fluent_promotions', null=True, verbose_name='categories', to='publication_backbone.Category', blank=True)),
            ],
            options={
                'db_table': 'contentitem_promo_promopluginmodel',
                'verbose_name': 'Promo Plugin',
                'verbose_name_plural': 'Promo Plugins',
            },
            bases=('fluent_contents.contentitem',),
        ),
    ]
