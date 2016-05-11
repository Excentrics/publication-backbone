# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PublicationBackboneConfig(AppConfig):
    name = 'publication_backbone'
    verbose_name = _('Publication backbone')

    def ready(self):
        # import signal handlers
        import publication_backbone.signals.handlers


class InterviewConfig(AppConfig):
    name = 'publication_backbone.interview'
    verbose_name = _('Interview designer')


class QuizConfig(AppConfig):
    name = 'publication_backbone.quiz'
    verbose_name = _('Quiz designer')


js_trans_dict = [
            _('now')
        ,   _('week')
        ,   _('week ago')
        ,   _('month')
        ,   _('month ago')
        ,   _('year')
        ,   _('year ago')
        ,   _('past')

]