# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_contents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SitemapItem',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem')),
                ('template', models.CharField(default=(b'publication_backbone/plugins/sitemap/default.html', 'Default sitemap'), max_length=255, verbose_name='Template', choices=[(b'publication_backbone/plugins/sitemap/default.html', 'Default sitemap')])),
            ],
            options={
                'db_table': 'contentitem_sitemap_sitemapitem',
                'verbose_name': 'Sitemap',
                'verbose_name_plural': 'Sitemaps',
            },
            bases=('fluent_contents.contentitem',),
        ),
    ]
