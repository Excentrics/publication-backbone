# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import publication_backbone.utils.media


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_contents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentGapItem',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem')),
                ('css_class', models.CharField(help_text='CSS class for container', max_length=255, verbose_name='CSS class', blank=True)),
                ('attributes', models.CharField(help_text='Attributes for container', max_length=255, verbose_name='Attributes', blank=True)),
                ('image', models.ImageField(help_text='Image for container background', upload_to=publication_backbone.utils.media.get_media_path, verbose_name='Background image', blank=True)),
            ],
            options={
                'db_table': 'contentitem_content_gap_contentgapitem',
                'verbose_name': 'Content gap',
                'verbose_name_plural': 'Content gaps',
            },
            bases=('fluent_contents.contentitem',),
        ),
    ]
