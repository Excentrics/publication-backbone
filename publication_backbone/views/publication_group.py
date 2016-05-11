# -*- coding: utf-8 -*-
from django.views.generic.list import MultipleObjectTemplateResponseMixin, BaseListView
from django.views.generic.detail import BaseDetailView, SingleObjectTemplateResponseMixin
from django.conf import settings
from django.core.paginator import EmptyPage

from publication_backbone.models import PublicationGroup
from publication_backbone.utils.paginator import Paginator, OffsetNotAnInteger
from publication_backbone.views.mixins import (
    JSONSingleObjectTemplateResponseMixin,
    JSONMultipleObjectTemplateResponseMixin
    )
from publication_backbone import conf as config

from constance import config as old_config



try:
    ITEMS_COUNT = old_config.PUBLICATION_BACKBONE_ITEMS_COUNT
except:
    ITEMS_COUNT = 10




#==============================================================================
# PublicationGroupHybridDetailView
#==============================================================================
class PublicationGroupHybridDetailView(JSONSingleObjectTemplateResponseMixin, SingleObjectTemplateResponseMixin, BaseDetailView):

    def __init__(self, **kwargs):
        self.model = kwargs.get('model') or PublicationGroup
        self.queryset = self.model.objects.all()
        super(PublicationGroupHybridDetailView, self).__init__(**kwargs)


    #@method_decorator(never_ever_cache)
    def dispatch(self, *args, **kwargs):

        # Try looking up by primary key and patch it.
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        if pk is not None:
            self.kwargs[self.pk_url_kwarg] = kwargs[self.pk_url_kwarg] = self.model.get_pk_by_publication_reference(pk)

        return super(PublicationGroupHybridDetailView, self).dispatch(*args, **kwargs)

    def render_to_response(self, context):
        # Look for a 'format=json' REQUEST argument
        if self.request.REQUEST.get('format','html') == 'json':
            return JSONSingleObjectTemplateResponseMixin.render_to_response(self, context)
        else:
            return SingleObjectTemplateResponseMixin.render_to_response(self, context)

    def get_context_data(self, **kwargs):
        context = super(PublicationGroupHybridDetailView, self).get_context_data(**kwargs)
        thumbnail_geometry = (config.PUBLICATION_BACKBONE_CATALOG_THUMBNAIL_WIDTH, config.PUBLICATION_BACKBONE_CATALOG_THUMBNAIL_HEIGHT)
        context.update({
            'thumbnail_geometry': "x".join(str(x) for x in thumbnail_geometry),
            'thumbnail_background': config.PUBLICATION_BACKBONE_CATALOG_THUMBNAIL_BACKGROUND,
        })
        return context


#==============================================================================
# PublicationGroupHybridListView
#==============================================================================
class PublicationGroupHybridListView(
    JSONMultipleObjectTemplateResponseMixin,
    MultipleObjectTemplateResponseMixin,
    BaseListView):

    initial_data = {}
    paginator_class = Paginator
    paginate_by = ITEMS_COUNT

    def __init__(self, **kwargs):
        self.model = kwargs.get('model') or PublicationGroup
        super(PublicationGroupHybridListView, self).__init__(**kwargs)

    def render_to_response(self, context):
        # Look for a 'format=json' REQUEST argument
        frmt = self.initial_data.get('format') or self.request.REQUEST.get('format', 'html')
        if frmt == 'json':
            return JSONMultipleObjectTemplateResponseMixin.render_to_response(self, context)
        else:
            return MultipleObjectTemplateResponseMixin.render_to_response(self, context)

    def paginate_queryset(self, queryset, page_size):
        """
        Paginate the queryset, if needed.
        """
        limit = self.kwargs.get('limit') or self.request.REQUEST.get('limit')
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            limit = page_size
        limit = min(limit, getattr(settings, "MAX_LIMIT_PER_PAGE",  500))
        orphans = self.kwargs.get('orphans') or self.request.REQUEST.get('orphans') or getattr(settings, "ORPHANS",  0)
        paginator = self.get_paginator(queryset, limit, orphans=orphans, allow_empty_first_page=self.get_allow_empty())
        offset = self.kwargs.get('offset') or self.request.REQUEST.get('offset', 0)
        try:
            page = paginator.page_by_offset(offset)
        except OffsetNotAnInteger:
            # If page is not an integer, deliver first page.
            page = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            page = paginator.page(paginator.num_pages)
        return (paginator, page, page.object_list, page.has_other_pages())

    def get_context_data(self, **kwargs):
        context = super(PublicationGroupHybridListView, self).get_context_data(**kwargs)
        thumbnail_geometry = (config.PUBLICATION_BACKBONE_CATALOG_THUMBNAIL_WIDTH, config.PUBLICATION_BACKBONE_CATALOG_THUMBNAIL_HEIGHT)
        context.update({
            'thumbnail_geometry': "x".join(str(x) for x in thumbnail_geometry),
            'thumbnail_width': thumbnail_geometry[0],
            'thumbnail_height': thumbnail_geometry[1],
            'thumbnail_background': config.PUBLICATION_BACKBONE_CATALOG_THUMBNAIL_BACKGROUND,
        })
        return context