# -*- coding: utf-8 -*-
from django.views.generic.detail import BaseDetailView, SingleObjectTemplateResponseMixin
from django.views.generic.list import BaseListView, MultipleObjectTemplateResponseMixin
#from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView
from publication_backbone.models import Rubric, Category
from publication_backbone.models_bases.rubricator import RubricInfo
from publication_backbone.views.mixins import (
    JSONSingleObjectTemplateResponseMixin,
    JSONMultipleObjectTemplateResponseMixin,
    JSMultipleObjectTemplateResponseMixin
    )
from publication_backbone.utils.cache import never_ever_cache


#==============================================================================
# RubricHybridDetailView
#==============================================================================
class RubricHybridDetailView(JSONSingleObjectTemplateResponseMixin, SingleObjectTemplateResponseMixin, BaseDetailView):

    def __init__(self, **kwargs):
        self.model = kwargs.get('model') or Rubric
        super(RubricHybridDetailView, self).__init__(**kwargs)

    def render_to_response(self, context):
        # Look for a 'format=json' REQUEST argument
        if self.request.REQUEST.get('format','html') == 'json':
            return JSONSingleObjectTemplateResponseMixin.render_to_response(self, context)
        else:
            return SingleObjectTemplateResponseMixin.render_to_response(self, context)


import time

#==============================================================================
# RubricHybridListView
#==============================================================================
class RubricHybridListView(JSONMultipleObjectTemplateResponseMixin,
                               JSMultipleObjectTemplateResponseMixin,
                               MultipleObjectTemplateResponseMixin,
                               BaseListView):

    initial_data = {}

    def __init__(self, **kwargs):
        self.model = kwargs.get('model') or Rubric
        super(RubricHybridListView, self).__init__(**kwargs)

    def render_to_response(self, context):
        # Look for a 'format=json' REQUEST argument
        frmt = self.initial_data.get('format') or self.request.REQUEST.get('format', 'html')
        if frmt == 'json':
            return JSONMultipleObjectTemplateResponseMixin.render_to_response(self, context)
        elif frmt == 'js':
            return never_ever_cache(JSMultipleObjectTemplateResponseMixin.render_to_response)(self, context)
        else:
            return MultipleObjectTemplateResponseMixin.render_to_response(self, context)

    def get_set(self):
        raw_set = self.kwargs.get('set')
        raw_set = [] if raw_set is None else raw_set.split(';')
        set = []
        for x in raw_set:
            try:
                set.append(long(str(x)))
            except (ValueError, TypeError):
                continue
        return set

    def get_category(self):
        selected_pk = self.kwargs.get('selected') or self.request.REQUEST.get('selected')
        if selected_pk:
            category = get_object_or_404(Category, pk=selected_pk)
        else:
            path = self.kwargs.get('path')
            if path:
                category = get_object_or_404(Category, path=path)
            else:
                category = None
        return category

    def get_queryset(self):

        self.set = self.get_set()
        self.category = self.get_category()
        self.trunk = self.category.rubrics.active().values_list('id', flat=True) if self.category else []

        return super(RubricHybridListView, self).get_queryset().toplevel().active()

    def get_context_data(self, **kwargs):
        set = self.set
        if self.trunk:
            set.extend(self.trunk)
            trunk = RubricInfo.cached_decompress(self.model, self.trunk, fix_it=True)
        else:
            trunk = RubricInfo.cached_decompress(self.model, self.get_queryset().values_list('id', flat=True), fix_it=True)

        tree = RubricInfo.cached_decompress(self.model, set, fix_it=True)
        tree.root.attrs['trunk'] = True
        for k, v in trunk.items():
            x = tree.get(k)
            if not x is None:
                if v.is_leaf:
                    x.attrs['branch'] = True
                else:
                    x.attrs['trunk'] = True

        context = super(RubricHybridListView, self).get_context_data(**kwargs)
        context.update({'root': tree.root,
                        'name': self.model._meta.object_name.lower(),
                        'category': self.category
        })

        return context

#============================================
# View to render js requirements to CategoryHybridListView
#============================================
class RubricatorCommonJsView(TemplateView):
    content_type = 'application/javascript'
    template_name = 'publication_backbone/rubricator/rubricator_common.js'

    def get_context_data(self, **kwargs):
        context = super(RubricatorCommonJsView, self).get_context_data(**kwargs)
        context.update({'rubricator_name': Rubric._meta.object_name.lower()})
        return context
