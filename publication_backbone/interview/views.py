# -*- coding: utf-8 -*-
from django.views.generic.detail import BaseDetailView
from django.views.generic.base import TemplateResponseMixin
from .models import InterviewItem
from django.utils import timezone
from django.http import Http404
from django.utils.translation import ugettext as _
import json


class InterviewView(TemplateResponseMixin, BaseDetailView):

    http_method_names = ['post',]
    template_name = 'publication_backbone/interview/interview.json'
    content_type = 'application/json'
    model = InterviewItem


    def post(self, request, *args, **kwargs):

        try:

            body = json.loads(self.request.body)
            answer_id = body["answerId"]
            self.object = self.get_object()
            interview = self.object.interview
            if interview.date_end > timezone.now():
                question = interview.interviewquestion_set.get(pk=answer_id)
                question.vote()
            else:
                raise Http404(_("Page not found"))

            context = {
                'object': self.object,
                'questions': interview.get_questions(),
                'interviewed_count': interview.interviewed_count
            }
            return self.render_to_response(context)

        except:

            raise Http404(_("Page not found"))



