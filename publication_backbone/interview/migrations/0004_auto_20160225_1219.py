# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interview', '0003_interviewitem'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='interviewquestion',
            options={'verbose_name': 'interview answer', 'verbose_name_plural': 'interview answers'},
        ),
        migrations.AlterField(
            model_name='interviewitem',
            name='interview',
            field=models.ForeignKey(verbose_name='interview', to='interview.Interview'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='interviewquestion',
            name='count',
            field=models.PositiveIntegerField(default=0, verbose_name='Answers count'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='interviewquestion',
            name='interview',
            field=models.ForeignKey(verbose_name='interview', to='interview.Interview'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='interviewquestion',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Possible answer'),
            preserve_default=True,
        ),
    ]
