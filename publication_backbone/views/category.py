# -*- coding: utf-8 -*-
from django.views.generic.detail import BaseDetailView, SingleObjectTemplateResponseMixin
from django.views.generic.list import BaseListView, MultipleObjectTemplateResponseMixin
from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404

from publication_backbone.models import BaseCategory
from publication_backbone.views.mixins import (
    JSONSingleObjectTemplateResponseMixin,
    JSMultipleObjectTemplateResponseMixin,
    JSONMultipleObjectTemplateResponseMixin)
from publication_backbone.utils.cache import never_ever_cache
from publication_backbone import conf as config

#==============================================================================
# CategoryHybridDetailView
#==============================================================================
class CategoryHybridDetailView(JSONSingleObjectTemplateResponseMixin, SingleObjectTemplateResponseMixin, BaseDetailView):

    def __init__(self, **kwargs):
        self.model = kwargs.get('model') or BaseCategory
        super(CategoryHybridDetailView, self).__init__(**kwargs)

    def render_to_response(self, context):
        # Look for a 'format=json' REQUEST argument
        if self.request.REQUEST.get('format','html') == 'json':
            return JSONSingleObjectTemplateResponseMixin.render_to_response(self, context)
        else:
            return SingleObjectTemplateResponseMixin.render_to_response(self, context)


#==============================================================================
# CategoryHybridListView
#==============================================================================
class CategoryHybridListView(
    JSONMultipleObjectTemplateResponseMixin,
    JSMultipleObjectTemplateResponseMixin,
    MultipleObjectTemplateResponseMixin,
    BaseListView):

    initial_data = {}

    def __init__(self, **kwargs):
        self.model = kwargs.get('model') or BaseCategory
        super(CategoryHybridListView, self).__init__(**kwargs)

    def render_to_response(self, context):
        # Look for a 'format=json' REQUEST argument
        frmt = self.initial_data.get('format') or self.request.REQUEST.get('format', 'html')
        if frmt == 'json':
            return JSONMultipleObjectTemplateResponseMixin.render_to_response(self, context)
        elif frmt == 'js':
            return never_ever_cache(JSMultipleObjectTemplateResponseMixin.render_to_response)(self, context)
        else:
            return MultipleObjectTemplateResponseMixin.render_to_response(self, context)

    def get_menu_orientation(self):
        menu_orientation = self.kwargs.get('menu_orientation') or \
                           self.request.REQUEST.get('menu_orientation') or \
                           config.PUBLICATION_BACKBONE_CATEGORY_MENU_ORIENTATION.strip()
        return menu_orientation

    def get_category(self):
        selected_pk = self.kwargs.get('selected') or self.request.REQUEST.get('selected')
        if selected_pk:
            category = get_object_or_404(BaseCategory, pk=selected_pk)
        else:
            path = self.kwargs.get('path')
            if path:
                category = get_object_or_404(BaseCategory, path=path)
            else:
                category = None
        return category

    def get_queryset(self):
        self.category = self.get_category()
        self.menu_orientation = self.get_menu_orientation()
        queryset = super(CategoryHybridListView, self).get_queryset().visible()
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CategoryHybridListView, self).get_context_data(**kwargs)
        context.update({
            'category': self.category,
            'menu_orientation': self.menu_orientation
        })
        return context


#============================================
# View to render js requirements to CategoryHybridListView
#============================================
class CategoryCommonJsView(TemplateView):
    content_type = 'application/javascript'
    template_name = 'publication_backbone/category/category_common.js'

