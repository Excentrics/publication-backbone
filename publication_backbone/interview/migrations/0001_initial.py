# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Interview',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Question')),
                ('date_end', models.DateTimeField(verbose_name='Date end')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'interview',
                'verbose_name_plural': 'interviews',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InterviewQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='question')),
                ('count', models.PositiveIntegerField(default=0, verbose_name='answers count')),
                ('interview', models.ForeignKey(to='interview.Interview')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'interview question',
                'verbose_name_plural': 'interview questions',
            },
            bases=(models.Model,),
        ),
    ]
