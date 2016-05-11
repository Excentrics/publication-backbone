# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_contents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='YandexMapItem',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem')),
                ('caption', models.CharField(max_length=255, verbose_name='caption', blank=True)),
                ('address', models.CharField(max_length=255, verbose_name='address', blank=True)),
                ('latitude', models.CharField(max_length=25, verbose_name='latitude', blank=True)),
                ('longitude', models.CharField(max_length=25, verbose_name='longitude', blank=True)),
                ('zoom', models.PositiveIntegerField(default=15, verbose_name='zoom')),
                ('map_type', models.CharField(default=b'yandex#publicMap', max_length=50, verbose_name='map_type', choices=[(b'yandex#publicMap', 'public map'), (b'yandex#map', 'schema map'), (b'yandex#satellite', 'satellite map'), (b'yandex#hybrid', 'hybrid map')])),
                ('color', models.CharField(default=b'#FF0000', max_length=10, verbose_name='marker color', choices=[(b'#FF0000', 'red'), (b'#00FF00', 'green'), (b'#0000FF', 'blue'), (b'#FFED00', 'yellow')])),
                ('template', models.CharField(default=b'publication_backbone/plugins/yandex_map/default.html', max_length=255, verbose_name='Template', choices=[(b'publication_backbone/plugins/yandex_map/default.html', 'Default yandex map template')])),
            ],
            options={
                'db_table': 'contentitem_yandex_map_yandexmapitem',
                'verbose_name': 'Yandex Map',
                'verbose_name_plural': 'Yandex Maps',
            },
            bases=('fluent_contents.contentitem',),
        ),
    ]
