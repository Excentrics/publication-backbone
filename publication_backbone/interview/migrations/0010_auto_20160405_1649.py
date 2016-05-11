# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interview', '0009_auto_20160331_1815'),
    ]

    operations = [
        migrations.AddField(
            model_name='interview',
            name='final_text',
            field=models.TextField(help_text='Result final text', null=True, verbose_name='Final text', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='interviewitem',
            name='interview',
            field=models.ForeignKey(verbose_name='Question', to='interview.Interview'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='quizresult',
            name='quiz',
            field=models.ForeignKey(related_name='quiz', verbose_name='Quiz', to='interview.Quiz'),
            preserve_default=True,
        ),
    ]
