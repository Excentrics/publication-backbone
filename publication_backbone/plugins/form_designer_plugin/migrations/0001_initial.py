# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_contents', '0001_initial'),
        ('form_designer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FormDesignerLink',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem')),
                ('form_definition', models.ForeignKey(verbose_name='Form', to='form_designer.FormDefinition')),
            ],
            options={
                'db_table': 'contentitem_form_designer_plugin_formdesignerlink',
                'verbose_name': 'Form link',
                'verbose_name_plural': 'Form links',
            },
            bases=('fluent_contents.contentitem',),
        ),
    ]
