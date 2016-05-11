# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields
import re
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('publication_backbone', '0003_auto_20151207_1805'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaticPlaceholder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Placeholder title')),
                ('slug', models.CharField(help_text='Only in latin charset a-z', max_length=100, verbose_name='Placeholder name', validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')])),
                ('site', models.ForeignKey(to='sites.Site')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'placeholder',
                'verbose_name_plural': 'placeholders',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='staticplaceholder',
            unique_together=set([('name', 'site')]),
        ),
        migrations.AlterField(
            model_name='publication',
            name='comments_enabled',
            field=models.BooleanField(default=False, verbose_name='Comments enabled'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='publication',
            name='rubrics',
            field=mptt.fields.TreeManyToManyField(to='publication_backbone.Rubric', verbose_name='rubrics', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='publication',
            name='sub_name',
            field=models.CharField(max_length=255, null=True, verbose_name='sub name', blank=True),
            preserve_default=True,
        ),
    ]
