# -*- coding: utf-8 -*-
import types

from django.db import models, connections
from django.db.models import Count
from django.db.models.query import ValuesQuerySet
from django.utils.translation import ugettext_lazy as _

from polymorphic.query import PolymorphicQuerySet
from polymorphic.manager import PolymorphicManager

from publication_backbone.models_bases.polymorphic_mptt.managers import PolymorphicMPTTModelManager, PolymorphicMPTTQuerySet
from publication_backbone.models_bases.rubricator import RubricInfo
from publication_backbone.models_bases.aggregates import Dummy

from django.db.models import Q
from operator import __or__ as OR


#==============================================================================
# Queryset Mixins
#==============================================================================
class ActiveQuerySetMixin(object):

    def active(self):
        return self.filter(active=True)


class RangeQuerySetMixin(object):

    def in_ranges(self, ranges):
        queryset = self
        for key, value in ranges.items():
            if value:
                min, max = value

                if min is not None:
                    queryset = queryset.filter(models.Q(**{key + '__gte': min}))
                if max is not None:
                    queryset = queryset.filter(models.Q(**{key + '__lte': max}))
        return queryset


class SubjectAndRelationQuerySetMixin(object):

    def subject_and_relation(self, subj, rel=None):
        """
        :param: rel - object
            "b" - bidirectional
            "f" - forward
            "r" - reverse
        """
        queryset = self
        if rel is None:
            rel = {}
        rel_b, rel_f, rel_r = rel.get("b", [])[:], rel.get("f", [])[:], rel.get("r", [])[:]
        if rel_b:
            rel_f.extend(rel_b)
            rel_r.extend(rel_b)
        if rel_f or rel_r:
            if subj:
                if rel_r:
                    q_lst = [models.Q(forward_relations__to_publication__in=subj) &
                             models.Q(forward_relations__rubric__in=rel_r), ]
                else:
                    q_lst = []
                if rel_f:
                    q_lst.append(models.Q(backward_relations__from_publication__in=subj) &
                                 models.Q(backward_relations__rubric__in=rel_f))
                queryset = queryset.filter(reduce(OR, q_lst)).distinct()
            else:
                queryset = queryset.filter(models.Q(forward_relations__rubric__in=rel_f) |
                                           models.Q(backward_relations__rubric__in=rel_r)).distinct()
        elif subj:
            queryset = queryset.filter(models.Q(forward_relations__to_publication__in=subj) |
                                       models.Q(backward_relations__from_publication__in=subj)).distinct()
        return queryset


class OrderByNameAscQuerySetMixin(object):

    def order_by_name_asc(self):
        return self.order_by('name')


class OrderByNameDescQuerySetMixin(object):

    def order_by_name_desc(self):
        return self.order_by('-name')


class OrderByDateAddedAscQuerySetMixin(object):

    def order_by_date_added_asc(self):
        return self.order_by('date_added')


class OrderByDateAddedDescQuerySetMixin(object):

    def order_by_date_added_desc(self):
        return self.order_by('-date_added')


class OrderByLastModifiedAscQuerySetMixin(object):

    def order_by_last_modified_asc(self):
        return self.order_by('last_modified')


class OrderByLastModifiedDescQuerySetMixin(object):

    def order_by_last_modified_desc(self):
        return self.order_by('-last_modified')

#==============================================================================
# Querysets
#==============================================================================
class RubricQuerySet(ActiveQuerySetMixin, PolymorphicMPTTQuerySet):
    """
    Rubric queryset
    """
    def attribute_is_characteristic_or_mark(self):
        return self.filter(Q(attribute_mode=self.model.ATTRIBUTE_IS_CHARACTERISTIC) |
                           Q(attribute_mode=self.model.ATTRIBUTE_IS_MARK))

    def attribute_is_relation(self):
        return self.filter(attribute_mode=self.model.ATTRIBUTE_IS_RELATION)

    def hard_delete(self):
        return super(RubricQuerySet, self).delete()

    def delete(self):
        return super(RubricQuerySet, self.exclude(system_flags=self.model.system_flags.delete_restriction)).delete()


class BaseCategoryQuerySet(PolymorphicMPTTQuerySet):
    """
    Base Category queryset
    """
    def visible(self):
        return self.filter(visible=True)


class CategoryQuerySet(BaseCategoryQuerySet):
    """
    Category queryset
    """
    pass


class PublicationQuerySet(
    SubjectAndRelationQuerySetMixin,
    RangeQuerySetMixin,
    ActiveQuerySetMixin,
    OrderByNameAscQuerySetMixin,
    OrderByNameDescQuerySetMixin,
    OrderByDateAddedAscQuerySetMixin,
    OrderByDateAddedDescQuerySetMixin,
    #OrderByLastModifiedAscQuerySetMixin,
    OrderByLastModifiedDescQuerySetMixin,
    PolymorphicQuerySet
    ):
    """
    Publication queryset
    """

    ORDER_BY_NAME_ASC = 'name_asc'
    ORDER_BY_NAME_DESC = 'name_desc'

    ORDER_BY_DATE_ADDED_ASC = 'date_added_asc'
    ORDER_BY_DATE_ADDED_DESC = 'date_added_desc'

    ORDERING_MODES = {
        ORDER_BY_NAME_ASC: (OrderByNameAscQuerySetMixin.order_by_name_asc, _('Alphabetical')),
        ORDER_BY_NAME_DESC: (OrderByNameDescQuerySetMixin.order_by_name_desc, _('Alphabetical: descending')),
        ORDER_BY_DATE_ADDED_ASC: (OrderByDateAddedAscQuerySetMixin.order_by_date_added_asc, _('Date Added: old first')),
        ORDER_BY_DATE_ADDED_DESC: (OrderByDateAddedDescQuerySetMixin.order_by_date_added_desc, _('Date Added: new first')),
        #ORDER_BY_LAST_MODIFIED_ASC: (OrderByLastModifiedAscQuerySetMixin.order_by_last_modified_asc, _('Last Modified: old first')),
        #ORDER_BY_LAST_MODIFIED_DESC: (OrderByLastModifiedDescQuerySetMixin.order_by_last_modified_desc, _('Last Modified: new first')),
    }

    # ordering
    def make_ordering(self, order_by):
        ordering_mode = self.ORDERING_MODES.get(order_by)
        if ordering_mode:
            return ordering_mode[0](self)
        else:
            return self

    def get_ordering_modes(self):
        return [{'id': k, 'name': v[1]} for (k, v) in self.ORDERING_MODES.items()]

    # filtering
    def make_filtering(self, set=None, use_cached_decompress=False, meta=None, field_name='rubrics'):
        rubrics_model = self.model._meta.get_field(field_name).rel.to
        if use_cached_decompress:
            tree = RubricInfo.cached_decompress(rubrics_model, set, fix_it=True)
        else:
            tree = RubricInfo.decompress(rubrics_model, set, fix_it=True)
        filters = tree.root.rubric.get_real_instance().make_filters(rubric_info=tree.root, field_name=field_name)
        if not meta is None:
            meta["tree_info"] = tree
        if filters:
            result = self.filter(filters[0])
            for x in filters[1:]:
                result = result.filter(x)
            return result.distinct()
        else:
            return self

    def try_merge_to_group(self, group=None):
        queryset = self
        group_model = self.model.group.field.rel.to
        if group_model.objects.exists():
            if group:
                queryset = queryset.filter(group=group)
            else:
                # merge items and add count per group
                queryset_with_counts = queryset.with_counts(count_field='num_objects')
                # ungroup if needed
                if queryset_with_counts.count() > 1:
                    queryset = queryset_with_counts
        return queryset

    # merge items and add count per group
    def with_counts(self, group_field='grp', count_field=None):
        if not count_field:
            count_field = 'num_%ss' % self.model._meta.object_name.lower()
        queryset = self.values(group_field).annotate(**{count_field: Count(self.model._meta.pk.name, distinct=True)})
        return queryset

    # make PublicationQuerySet from ValuesQuerySet
    def from_values_query_set(self, queryset):
        if isinstance(queryset, ValuesQuerySet):
            fields = [(field.name, field.get_attname_column()[1]) for field in self.model._meta.fields if field.name not in queryset.field_names]
            for name, db_name in fields:
                queryset = queryset.annotate(**{db_name: Dummy(name)})
            raw_query, query_params = queryset.query.get_compiler(self.db).as_sql()
            queryset = self.model.objects.raw(raw_query, params=query_params) if raw_query else self.model.objects.none()
        return queryset

    def get_real_rubrics_ids(self):
        # Pythonic, but working to slow, use connection.ops.quote_name monkey-path
        """
        result = self.model.rubrics.through.objects.\
            filter(publication_id__in=self.values_list('pk', flat=True)).distinct().values_list('rubric_id', flat=True)

        """
        # Re-support subqueries by disabling the auto-quote feature with the following monkey-patch
        db_ops = connections[self.db].ops
        if not hasattr(db_ops, '_MP_quote_name'):
            db_ops._MP_quote_name = db_ops.quote_name
            db_ops.quote_name = types.MethodType(
                lambda self, name: name if name.startswith('(') else self._MP_quote_name(name), db_ops)

        # Make queryset
        model = self.model.rubrics.through
        inner_alias = self.query.get_initial_alias() + "_after_filtering"
        outer_qs = model.objects.distinct().values_list('rubric_id', flat=True)
        outer_alias = outer_qs.query.get_initial_alias()
        inner_qs = self.order_by().values_list('pk', flat=True)
        raw_subquery, subquery_params = inner_qs.query.get_compiler(self.db).as_sql()
        result = outer_qs.extra(
            tables=['({select}) AS {alias}'.format(
                select=raw_subquery,
                alias=inner_alias
            )],
            where=['{outer_alias}.publication_id = {inner_alias}.id'.format(
                outer_alias=outer_alias,
                inner_alias=inner_alias
            )],
            params=subquery_params
        )

        return result

class PublicationGroupQuerySet(PolymorphicQuerySet):
    """
    PublicationGroup queryset
    """
    pass

'''
class PublicationOptionQuerySet(PolymorphicQuerySet):
    """
    PublicationOption queryset
    """
    pass
'''

class ShippingQuerySet(ActiveQuerySetMixin, PolymorphicQuerySet):
    """
    Shipping queryset
    """
    pass


#==============================================================================
# Rubric
#==============================================================================
class RubricManager(PolymorphicMPTTModelManager):
    """
    A more classic manager for Rubric filtering and manipulation.
    """
    #: The queryset class to use.
    queryset_class = RubricQuerySet


#==============================================================================
# Base Category
#==============================================================================
class BaseCategoryManager(PolymorphicMPTTModelManager):
    """
    A more classic manager for Category filtering and manipulation.
    """
    #: The queryset class to use.
    queryset_class = BaseCategoryQuerySet

#==============================================================================
# Category
#==============================================================================
class CategoryManager(PolymorphicMPTTModelManager):
    """
    A more classic manager for Category filtering and manipulation.
    """
    #: The queryset class to use.
    queryset_class = CategoryQuerySet


#==============================================================================
# Publication
#==============================================================================
class PublicationManager(PolymorphicManager):
    """
    A more classic manager for Category filtering and manipulation.
    """
    #: The queryset class to use.
    queryset_class = PublicationQuerySet

    def active(self):
        return self.filter(active=True)


#==============================================================================
# PublicationGroup
#==============================================================================
class PublicationGroupManager(PolymorphicManager):
    """
    """
    #: The queryset class to use.
    queryset_class = PublicationGroupQuerySet

