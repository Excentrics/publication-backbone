# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.views.generic.list import MultipleObjectTemplateResponseMixin, BaseListView
from django.views.generic.detail import BaseDetailView, SingleObjectTemplateResponseMixin
from django.views.generic.base import TemplateView
from django.core.paginator import EmptyPage
from django.db.models import Max, Min

from publication_backbone.views.mixins import (
    JSONSingleObjectTemplateResponseMixin,
    JSONMultipleObjectTemplateResponseMixin,
    JSMultipleObjectTemplateResponseMixin
    )
from publication_backbone.models import Category, Rubric, Publication, PublicationGroup
from publication_backbone.utils.paginator import Paginator, OffsetNotAnInteger
from publication_backbone.models_bases.managers import PublicationQuerySet
from publication_backbone.utils.cache import never_ever_cache
from publication_backbone.utils.contrib import hash_unsorted_list, create_hash
from publication_backbone import conf as config
from datetime import datetime, time
from time import mktime
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.syndication.views import Feed


#==============================================================================
# PublicationHybridDetailView
#==============================================================================
class PublicationHybridDetailView(JSONSingleObjectTemplateResponseMixin, SingleObjectTemplateResponseMixin, BaseDetailView):

    def __init__(self, **kwargs):
        self.model = kwargs.get('model') or Publication
        self.queryset = self.model.objects.all()
        super(PublicationHybridDetailView, self).__init__(**kwargs)

    #@method_decorator(never_ever_cache)
    def dispatch(self, *args, **kwargs):
        # Try looking up by primary key and patch it.
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        if pk is not None:
            self.kwargs[self.pk_url_kwarg] = kwargs[self.pk_url_kwarg] = self.model.get_pk_by_publication_reference(pk)
        return super(PublicationHybridDetailView, self).dispatch(*args, **kwargs)

    def render_to_response(self, context):
        # Look for a 'format=json' REQUEST argument
        if self.request.REQUEST.get('format','html') == 'json':
            return JSONSingleObjectTemplateResponseMixin.render_to_response(self, context)
        else:
            response = SingleObjectTemplateResponseMixin.render_to_response(self, context)
            response['Last-Modified'] = self.object.last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT")
            return response

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

    def get_object(self, queryset=None):
        obj = super(PublicationHybridDetailView, self).get_object(queryset)
        self.category = self.get_category()
        if not(self.category and self.category.visible):
            self.category = obj.get_category()
        return obj

    def get_context_data(self, **kwargs):
        context = super(PublicationHybridDetailView, self).get_context_data(**kwargs)
        thumbnail_geometry = (config.PUBLICATION_BACKBONE_CATALOG_THUMBNAIL_WIDTH, config.PUBLICATION_BACKBONE_CATALOG_THUMBNAIL_HEIGHT)
        context.update({
            'name': self.model._meta.object_name.lower(),
            'category': self.category,
            'thumbnail_geometry': "x".join(str(x) for x in thumbnail_geometry),
            'thumbnail_background': config.PUBLICATION_BACKBONE_CATALOG_THUMBNAIL_BACKGROUND,
        })
        return context


#==============================================================================
# PublicationListHybridView
#==============================================================================
class PublicationListHybridView(
                         JSONMultipleObjectTemplateResponseMixin,
                         JSMultipleObjectTemplateResponseMixin,
                         MultipleObjectTemplateResponseMixin,
                         BaseListView,
                         ):
    initial_data = {}
    paginator_class = Paginator

    def __init__(self, **kwargs):
        model = kwargs.get('model')
        self.model = model if model else Publication
        self.queryset = self.model.objects.all()
        super(PublicationListHybridView, self).__init__(**kwargs)

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

    def get_ranges(self, ranges_names):

        raw_ranges = [(x, self.request.REQUEST.get(x, '').split(';')) for x in ranges_names if self.request.REQUEST.has_key(x)]
        ranges = {}
        for key, value in raw_ranges:
            if len(value) < 2:
                value.append(value[0])
            for i in range(2):
                try:
                    value[i] = float(value[i])
                except (ValueError, TypeError):
                    value[i] = None
            ranges[key] = {
                'value': value
            }

        return ranges

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

    def get_publication_group(self):
        raw_group_pk = self.kwargs.get('group_id') or self.request.REQUEST.get('group_id')
        if raw_group_pk:
            group = get_object_or_404(PublicationGroup, pk=PublicationGroup.get_pk_by_publication_reference(raw_group_pk))
        else:
            group = None
        return group

    def get_raw_order_by(self):
        return self.kwargs.get('order_by') or self.request.REQUEST.get('order_by') or config.PUBLICATION_BACKBONE_CATALOG_ORDER_BY

    def get_subj(self):
        raw_subj = self.kwargs.get('subj')
        raw_subj = [] if raw_subj is None else raw_subj.split(';')
        subj_ids = []
        for x in raw_subj:
            try:
                subj_ids.append(long(str(x)))
            except (ValueError, TypeError):
                continue
        subj = list(Publication.objects.active().filter(pk__in=subj_ids)) if subj_ids else []
        return subj

    def get_rel(self):
        raw_rel = self.kwargs.get('rel')
        raw_rel = [] if raw_rel is None else raw_rel.split(';')
        rel_b_ids, rel_f_ids, rel_r_ids = [], [], []
        for x in raw_rel:
            i = x.find('b')
            if i != -1:
                try:
                    rel_b_ids.append(long(str(x[:i] + x[i + 1:])))
                except (ValueError, TypeError):
                    continue
            else:
                i = x.find('f')
                if i != -1:
                    try:
                        rel_f_ids.append(long(str(x[:i] + x[i + 1:])))
                    except (ValueError, TypeError):
                        continue
                else:
                    i = x.find('r')
                    if i != -1:
                        try:
                            rel_r_ids.append(long(str(x[:i] + x[i + 1:])))
                        except (ValueError, TypeError):
                            continue
                    else:
                        try:
                            rel_b_ids.append(long(str(x)))
                        except (ValueError, TypeError):
                            continue
        return {"b": list(Rubric.objects.active().attribute_is_relation().filter(pk__in=rel_b_ids)) if rel_b_ids else [],
                "f": list(Rubric.objects.active().attribute_is_relation().filter(pk__in=rel_f_ids)) if rel_f_ids else [],
                "r": list(Rubric.objects.active().attribute_is_relation().filter(pk__in=rel_r_ids)) if rel_r_ids else []}

    def get_potential_rubrics_ids(self):
        trunk_tree_info = self.meta_trunk["tree_info"]
        key = Publication.POTENTIAL_RUBRICS_IDS_CACHE_KEY_PATTERN % {'tree_hash': trunk_tree_info.get_hash()}
        rubrics_ids = cache.get(key, None)
        if rubrics_ids is None:
            rubrics_ids = trunk_tree_info.trim(self.potential_collection.get_real_rubrics_ids()).keys()
            cache.set(key, rubrics_ids, Publication.CACHE_TIMEOUT)
            buf = Publication.get_potential_rubrics_buffer()
            old_key = buf.record(key)
            if not old_key is None:
                cache.delete(old_key)
        return rubrics_ids

    def get_real_rubrics_ids(self):

        set_tree_info = self.meta_set["tree_info"]
        key = Publication.REAL_RUBRICS_IDS_CACHE_KEY_PATTERN % {
            'tree_hash': create_hash('.'.join([
                set_tree_info.get_hash(),
                hash_unsorted_list(self.subj) if self.subj else '',
                hash_unsorted_list(self.rel["b"]) if self.rel["b"] else '',
                hash_unsorted_list(self.rel["f"]) if self.rel["f"] else '',
                hash_unsorted_list(self.rel["r"]) if self.rel["r"] else ''
                ]))
        }
        rubrics_ids = cache.get(key, None)
        if rubrics_ids is None:
            rubrics_ids = set_tree_info.trim(self.real_collection.get_real_rubrics_ids()).keys()
            cache.set(key, rubrics_ids, Publication.CACHE_TIMEOUT)
            buf = Publication.get_real_rubrics_buffer()
            old_key = buf.record(key)
            if not old_key is None:
                cache.delete(old_key)
        return rubrics_ids

    def beautify_date_range(self, min_date, max_date):
        return datetime.combine(min_date, time.min), datetime.combine(max_date, time.max)

    def get_date_range(self):
        aggregates = self.potential_collection.aggregate(min_date=Min('date_added'), max_date=Max('date_added'))

        min_date = aggregates.get('min_date')
        max_date = aggregates.get('max_date')
        show_date_exists = self.potential_collection.filter(show_date=True).exists()

        # validate min and max dates
        timezone_now = timezone.now()
        if min_date is None:
            min_date = timezone_now
        if max_date is None:
            max_date = timezone_now
        if max_date < timezone_now:
            max_date = timezone_now

        # beautify date range: set time of min_date to 00:01, set time of max_date to 23:59
        bf_min_date, bf_max_date = self.beautify_date_range(min_date, max_date)

        # convert beautify datetime objects to timestamp and invert them for correct range slider render
        # (left border must be set on max_date, right border must be set on min_date)
        bf_timestamp_min_date, bf_timestamp_max_date = -mktime(bf_min_date.timetuple()), -mktime(bf_max_date.timetuple())

        if not self.ranges.has_key('date_added'):
            # initial: set inverted start and end timestamp dates
            self.ranges['date_added'] = {
                'value': [bf_timestamp_max_date, bf_timestamp_min_date]
            }
        else:
            # update: smart set dates interval
            self.ranges['date_added']['value'] = [
                min(max(self.ranges['date_added']['value'][0], bf_timestamp_max_date), bf_timestamp_min_date),
                max(min(self.ranges['date_added']['value'][1], bf_timestamp_min_date), bf_timestamp_max_date),
            ]

        # get potential ordering modes list
        self.ordering_modes = self.potential_collection.get_ordering_modes()
        raw_order_by = self.get_raw_order_by()
        order_by_tuple = self.potential_collection.ORDERING_MODES.get(raw_order_by)
        self.order_by = {'id': str(raw_order_by), 'name': order_by_tuple[1]} if order_by_tuple else None

        # correct ordering_modes list if start and end date is same date
        if min_date == max_date or not show_date_exists:
            self.ranges['date_added']['limit'] = [-mktime(max_date.timetuple()), -mktime(min_date.timetuple())]
            # cut date_added ordering
            self.ordering_modes = [x for x in self.ordering_modes
                if x['id'] not in [PublicationQuerySet.ORDER_BY_DATE_ADDED_ASC, PublicationQuerySet.ORDER_BY_DATE_ADDED_DESC]]
            # set order mode to last ordering mode
            #self.order_by = self.ordering_modes[len(self.ordering_modes)-1]
        else:
            # set range limit to inverted start and end timestamp dates
            self.ranges['date_added']['limit'] = [bf_timestamp_max_date, bf_timestamp_min_date]
        # hack for hide date ranges slider
        if not show_date_exists:
            self.ranges['date_added']['limit'][1] = self.ranges['date_added']['limit'][0]

        return self.ranges['date_added']['value']


    def get_queryset(self):

        self.ranges = self.get_ranges(['date_added',])
        self.category = self.get_category()
        self.publication_group = self.get_publication_group()

        self.trunk = self.category.rubrics.active().values_list('id', flat=True) if self.category else []

        self.set = self.get_set()

        self.initial_set = tuple(self.set)

        self.set.extend(self.trunk)

        queryset = super(PublicationListHybridView, self).get_queryset().active()

        self.subj = self.get_subj()

        self.rel = self.get_rel()

        self.meta_trunk, self.meta_set = {}, {}
        self.potential_collection = queryset.make_filtering(self.trunk, use_cached_decompress=True, meta=self.meta_trunk)

        # get dates range and convert borders from timestamp to datetime
        date_range_value = self.get_date_range()
        start_date, end_date = datetime.fromtimestamp(-date_range_value[1]), datetime.fromtimestamp(-date_range_value[0])

        queryset = self.real_collection = queryset.make_filtering(
            self.set, use_cached_decompress=True, meta=self.meta_set
        ).subject_and_relation(self.subj, self.rel).in_ranges({'date_added': [start_date, end_date]}).make_ordering(self.order_by['id'] if self.order_by else None)

        self.potential_rubrics_ids = self.get_potential_rubrics_ids()
        self.real_rubrics_ids = self.get_real_rubrics_ids()

        queryset = queryset.try_merge_to_group(group=self.publication_group)

        return queryset

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

    def get_paginate_by(self, queryset):
        """
        Get the number of items to paginate by, or ``None`` for no pagination.
        """
        return config.PUBLICATION_BACKBONE_CATALOG_PER_PAGE_ITEMS_COUNT

    def get_context_data(self, **kwargs):
        context = super(PublicationListHybridView, self).get_context_data(**kwargs)
        context['object_list'] = self.model.try_format_values_query_set(context['object_list'])
        rel = []
        for d, lst in self.rel.items():
            for obj in lst:
                obj.direction = d
                rel.append(obj)
        thumbnail_geometry = (config.PUBLICATION_BACKBONE_CATALOG_THUMBNAIL_WIDTH, config.PUBLICATION_BACKBONE_CATALOG_THUMBNAIL_HEIGHT)
        context.update({
            'category': self.category,
            'publication_group': self.publication_group,
            'name': self.model._meta.object_name.lower(),
            'rubricator_name': Rubric._meta.object_name.lower(),
            'ordering_modes': self.ordering_modes,
            'order_by': self.order_by,
            'ranges': self.ranges,
            'set': self.initial_set,
            'trunk': self.trunk,
            'subj': self.subj,
            'rel': rel,
            'thumbnail_geometry': "x".join(str(x) for x in thumbnail_geometry),
            'thumbnail_width': thumbnail_geometry[0],
            'thumbnail_height': thumbnail_geometry[1],
            'thumbnail_background': config.PUBLICATION_BACKBONE_CATALOG_THUMBNAIL_BACKGROUND,
            'potential_rubrics_ids': self.potential_rubrics_ids,
            'real_rubrics_ids': self.real_rubrics_ids,
            'today': -mktime(datetime.combine(timezone.now(), time.max).timetuple()),
        })
        return context




#============================================
# View to render js requirements to CategoryHybridListView
#============================================
class PublicationListCommonJsView(TemplateView):
    content_type = 'application/javascript'
    template_name = 'publication_backbone/catalog/catalog_common.js'




# RSS feed view
class PublicationRssFeed(Feed):
    title = _("RSS Feed title")
    link = "/"
    description = _("RSS Description title")

    def items(self):

        return Publication.objects.order_by('-date_added').active()[:config.PUBLICATION_RSS_FEED_COUNT]

    def item_title(self, item):
        return item.get_name()

    def item_description(self, item):
        return item.get_description()

    def item_link(self, item):
        return item.get_absolute_url()

    def item_categories(self, item):
        cats = []
        cat = item.get_category()
        if cat:
            cats.append(cat.get_name())

        return cats