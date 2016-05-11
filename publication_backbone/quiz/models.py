# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
import datetime
from future.utils import python_2_unicode_compatible
from future.builtins import str
from fluent_contents.models.db import ContentItem


class Quiz(models.Model):

    name = models.CharField(verbose_name=_('Name'), max_length=255)
    failure_text = models.CharField(verbose_name=_('Failure text'), help_text=_('Failure result text'), max_length=255, blank=False, default='')
    final_text = models.TextField(verbose_name=_('Final text'), help_text=_('Result final text'), blank=True, null=True)
    date_added = models.DateTimeField(default=datetime.datetime.now, verbose_name=_('Date added'))

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        abstract = False
        app_label = 'interview'
        verbose_name = _('Quiz')
        verbose_name_plural = _('Quizzes')
        ordering = ['date_added']


class QuizResult(models.Model):
    quiz = models.ForeignKey(Quiz, verbose_name=_("Quiz"), related_name='results')
    result_text = models.CharField(verbose_name=_('Text'), help_text=_('Result text'), max_length=600, blank=False)
    bound = models.PositiveIntegerField(verbose_name=_('Bound'), help_text=_('Min right question bound'), default=1, blank=False)

    class Meta:
        abstract = False
        app_label = 'interview'
        verbose_name = _('Quiz result')
        verbose_name_plural = _('Quiz results')


@python_2_unicode_compatible
class QuizItem(ContentItem):

    quiz = models.ForeignKey(Quiz, verbose_name=_("Quiz"))

    class Meta:
        verbose_name = _('Quiz')
        verbose_name_plural = _('Quizzes')

    def __str__(self):
        return str(self.quiz.name)

