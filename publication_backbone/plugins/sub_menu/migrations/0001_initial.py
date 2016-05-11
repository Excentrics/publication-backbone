# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_contents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubMenu',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem')),
                ('max_depth', models.PositiveIntegerField(default=1, verbose_name='Max depth')),
                ('template', models.CharField(default=(b'publication_backbone/plugins/sub_menu/default.html', 'Default sub menu'), max_length=255, verbose_name='Template', choices=[(b'publication_backbone/plugins/sub_menu/default.html', 'Default sub menu')])),
            ],
            options={
                'db_table': 'contentitem_sub_menu_submenu',
                'verbose_name': 'Sub menu',
                'verbose_name_plural': 'Sub menus',
            },
            bases=('fluent_contents.contentitem',),
        ),
    ]
