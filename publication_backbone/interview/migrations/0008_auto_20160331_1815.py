# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interview', '0007_quiz_quizresult'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quiz',
            name='default_bound',
        ),
        migrations.RemoveField(
            model_name='quiz',
            name='default_text',
        ),
        migrations.RemoveField(
            model_name='quizresult',
            name='text',
        ),
        migrations.AddField(
            model_name='quiz',
            name='failure_text',
            field=models.CharField(default='', help_text='Failure result text', max_length=255, verbose_name='Failure text'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='quiz',
            name='final_text',
            field=models.TextField(help_text='Result final text', null=True, verbose_name='Final text', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='quizresult',
            name='result_text',
            field=models.CharField(default='', help_text='Result text', max_length=600, verbose_name='Text'),
            preserve_default=False,
        ),
    ]
