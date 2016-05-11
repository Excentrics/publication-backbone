# -*- coding: utf-8 -*-
from django.conf import settings

from django.utils.translation import ugettext_lazy as _
from fluent_contents.extensions import ContentPlugin, plugin_pool
from models import QuizItem


@plugin_pool.register
class QuizPlugin(ContentPlugin):
    """
    Plugin for Quiz Block
    """
    model = QuizItem
    render_template = "publication_backbone/quiz/quiz.html"
    category = _('Advanced')
    raw_id_fields = ("quiz",)
    cache_output = not settings.DEBUG

    def get_context(self, request, instance, **kwargs):

        return {
            'instance': instance,
            'name': instance.quiz.name,
        }