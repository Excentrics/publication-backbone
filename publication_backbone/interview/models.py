# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
import time
import datetime
from future.utils import python_2_unicode_compatible
from future.builtins import str
from fluent_contents.models.db import ContentItem
from django.db.models import Sum


class Interview(models.Model):

    name = models.CharField(verbose_name=_('Question'), max_length=255)
    final_text = models.TextField(verbose_name=_('Final text'), help_text=_('Interview final text'), blank=True, null=True)
    date_added = models.DateTimeField(default=datetime.datetime.now, verbose_name=_('date added'))
    date_end = models.DateTimeField(verbose_name=_('Date end'), blank=False)

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        abstract = False
        app_label = 'interview'
        verbose_name = _('interview')
        verbose_name_plural = _('interviews')
        ordering = ['date_added']

    def get_questions(self):
        """
            Get all questions for this interview
        """
        answers = self.interviewquestion_set.all()
        total_answers = 0
        total_persent = 100
        i = 1
        for answer in answers:
            total_answers = total_answers + answer.get_count()
        if total_answers == 0:
            total_answers = 1
        total_count = answers.count()
        for answer in answers:
            if i < total_count:
                answer.perset_count = int( float(answer.get_count()) * 100 / total_answers)
                total_persent = total_persent - answer.perset_count
            else:
                answer.perset_count = total_persent
            i = i + 1

        return answers

    @property
    def interviewed_count(self):
        """
            Get count interviewed for this interview
        """
        total = self.interviewquestion_set.all().aggregate(Sum('count'))
        if total:
            total_answers = total.get("count__sum", 0)
        else:
            total_answers = 0

        return total_answers

    @property
    def is_up_to_date(self):
        """
            Check if interview is coming
        """
        date_end = time.mktime(self.date_end.timetuple())
        current_date = time.mktime(datetime.datetime.now().timetuple())
        if current_date > date_end:
            return False

        return True

class InterviewQuestion(models.Model):
    interview = models.ForeignKey(Interview, verbose_name=_("interview"))
    name = models.CharField(verbose_name=_('Possible answer'), max_length=255, blank=False)
    count = models.PositiveIntegerField(verbose_name=_('Answers count'), default=0, blank=False)
    is_right = models.BooleanField(verbose_name=_('Right answer'), default=False, blank=True)

    def get_name(self):
        return self.name

    def get_count(self):
        return self.count

    def vote(self):
        self.count = self.count + 1
        self.save()

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        abstract = False
        app_label = 'interview'
        verbose_name = _('interview answer')
        verbose_name_plural = _('interview answers')


@python_2_unicode_compatible
class InterviewItem(ContentItem):
    """
    Display a picture
    """

    interview = models.ForeignKey(Interview, verbose_name=_("Question"))

    class Meta:
        verbose_name = _('interview')
        verbose_name_plural = _('interviews')

    def __str__(self):
        return str(self.interview.name)

