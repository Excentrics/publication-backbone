# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fluent_contents', '0001_initial'),
        ('interview', '0007_quiz_quizresult'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuizItem',
            fields=[
                ('contentitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fluent_contents.ContentItem')),
                ('quiz', models.ForeignKey(verbose_name='Quiz', to='interview.Quiz')),
            ],
            options={
                'db_table': 'contentitem_quiz_quizitem',
                'verbose_name': 'Quiz',
                'verbose_name_plural': 'Quizzes',
            },
            bases=('fluent_contents.contentitem',),
        ),
    ]
