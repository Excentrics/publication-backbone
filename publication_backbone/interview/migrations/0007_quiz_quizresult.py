# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('interview', '0006_interviewquestion_is_right'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('default_text', models.CharField(help_text='Default result text', max_length=255, verbose_name='Result text')),
                ('default_bound', models.PositiveIntegerField(default=0, help_text='Default min right question bound', verbose_name='Default bound')),
                ('date_added', models.DateTimeField(default=datetime.datetime.now, verbose_name='Date added')),
                ('date_end', models.DateTimeField(null=True, verbose_name='Date end', blank=True)),
            ],
            options={
                'ordering': ['date_added'],
                'abstract': False,
                'verbose_name': 'Quiz',
                'verbose_name_plural': 'Quizzes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuizResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(help_text='Result text', max_length=255, verbose_name='Text')),
                ('bound', models.PositiveIntegerField(default=0, help_text='Min right question bound', verbose_name='Bound')),
                ('quiz', models.ForeignKey(verbose_name='Quiz', to='interview.Quiz')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Quiz result',
                'verbose_name_plural': 'Quiz results',
            },
            bases=(models.Model,),
        ),
    ]
