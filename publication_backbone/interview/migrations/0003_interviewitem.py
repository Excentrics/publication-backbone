# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_contents', '0001_initial'),
        ('interview', '0002_auto_20160125_1251'),
    ]

    operations = [
        migrations.CreateModel(
            name='InterviewItem',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem')),
                ('interview', models.ForeignKey(to='interview.Interview')),
            ],
            options={
                'db_table': 'contentitem_interview_interviewitem',
                'verbose_name': 'interview',
                'verbose_name_plural': 'interviews',
            },
            bases=('fluent_contents.contentitem',),
        ),
    ]
