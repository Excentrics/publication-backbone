# -*- coding: utf-8 -*-
from django.conf import settings

from django.utils.translation import ugettext_lazy as _
from fluent_contents.extensions import ContentPlugin, plugin_pool
from models import InterviewItem



@plugin_pool.register
class InterviewPlugin(ContentPlugin):
    """
    Plugin for Interview Block
    """
    model = InterviewItem
    render_template = "publication_backbone/interview/interview.html"
    raw_id_fields = ("interview",)
    category = _('Advanced')
    cache_output = not settings.DEBUG

    def get_context(self, request, instance, **kwargs):

        return {
            'instance': instance,
            'name': instance.interview.name,
            'questions': instance.interview.get_questions(),
            'interviewed_count': instance.interview.interviewed_count,
            'is_up_to_date': instance.interview.is_up_to_date
        }