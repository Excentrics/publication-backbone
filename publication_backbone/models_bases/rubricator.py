# -*- coding: utf-8 -*-
import datetime
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db import IntegrityError
from django.utils.encoding import force_unicode
from django.core.exceptions import ValidationError
from django.core.cache import cache

from bitfield import BitField
from mptt.exceptions import InvalidMove

from publication_backbone.utils.circular_buffer_in_cache import RingBuffer
from publication_backbone.utils.contrib import get_unique_slug, uniq, hash_unsorted_list
from publication_backbone.models_bases.polymorphic_mptt.models import (
    PolymorphicMPTTModel,
    PolymorphicTreeForeignKey,
    get_base_polymorphic_model,
    get_queryset_descendants,
    )



#==============================================================================
# Rubric
#==============================================================================
class BaseRubric(PolymorphicMPTTModel):
    """
    A model representing an Rubric.
    """
    CACHE_TIMEOUT = 3600
    RUBRIC_ACTIVE_CHILDREN_CACHE_KEY_PATTERN = 'rbrc_chldrn::%(id)d'
    RUBRIC_CHARACTERISTIC_DESCENDANTS_IDS_CACHE_KEY = 'rbrc_chrct_dscn_ids'
    RUBRIC_MARK_DESCENDANTS_IDS_CACHE_KEY = 'rbrc_mrk_dscn_ids'
    RUBRIC_ATTRIBUTES_ANCESTORS_CACHE_KEY_PATTERN = 'rbrc_attr_ancs::%(id)d::%(attribute_mode)d'


    DISPLAY_STANDARD = 10
    DISPLAY_EXTRA = 20
    DISPLAY_COLLAPSED = 30

    DISPLAY_MODES = (
        (DISPLAY_STANDARD, _('standard')),
        (DISPLAY_EXTRA, _('show extra')),
        (DISPLAY_COLLAPSED, _('show collapsed')),
    )

    ATTRIBUTE_IS_NONE = 0
    ATTRIBUTE_IS_CHARACTERISTIC = 10
    ATTRIBUTE_IS_MARK = 20
    ATTRIBUTE_IS_RELATION = 30

    ATTRIBUTE_MODES = (
        (ATTRIBUTE_IS_NONE, _('none')),
        (ATTRIBUTE_IS_CHARACTERISTIC, _('is characteristic')), # характеристика
        (ATTRIBUTE_IS_MARK, _('is mark')), # отметка
        (ATTRIBUTE_IS_RELATION, _('is relation')), # отношение
    )

    SYSTEM_FLAGS = {
        0: ('delete_restriction', _('Delete restriction')),
        1: ('change_parent_restriction', _('Change parent restriction')),
        2: ('change_slug_restriction', _('Change slug restriction')),
        3: ('change_subclass_restriction', _('Change subclass restriction')),
        4: ('has_child_restriction', _('Has child restriction')),
        5: ('tagged_restriction', _('Tagged restriction')),
    }

    parent = PolymorphicTreeForeignKey('self', verbose_name=_('parent'), null=True, blank=True, related_name='children',
                        db_index=True)
    name = models.CharField(verbose_name=_('name'), max_length=255)
    slug = models.SlugField(_("slug"), help_text=_("Used for URLs, auto-generated from name if blank"))
    path = models.CharField(verbose_name=_("path"), max_length=255, db_index=True, editable=False, unique=True)
    parent = PolymorphicTreeForeignKey('self', verbose_name=_('parent'), null=True, blank=True, related_name='children',
                        db_index=True)
    creation_date = models.DateTimeField(verbose_name=_('creation date'), db_index=True, default=datetime.datetime.now,
                                         editable=False)
    display_mode = models.PositiveSmallIntegerField(verbose_name=_('display mode'), choices=DISPLAY_MODES,
                                                    default=DISPLAY_STANDARD)
    active = models.BooleanField(verbose_name=_('active'), default=True, db_index=True)
    attribute_mode = models.PositiveSmallIntegerField(verbose_name=_('attribute mode'), choices=ATTRIBUTE_MODES,
                                                      default=ATTRIBUTE_IS_NONE, db_index=True,
                                                      help_text=_("Specifying mode of getting attributes for publication"))
    tags = models.CharField(verbose_name=_('tags'), max_length=255, null=True, blank=True,
                            help_text=_('Space delimited tags, for example: "red strikethrough"'))
    description = models.TextField(verbose_name=_('description'), null=True, blank=True)
    system_flags = BitField(flags=SYSTEM_FLAGS, verbose_name=_('system flags'), null=True, default=None)

    CLASSIFICATION_METHOD = (None, '')

    class Meta:
        abstract = True

    class MPTTMeta:
        order_insertion_by = ['creation_date']

    def __unicode__(self):
        return '%s' % self.name

    def get_ancestors_list(self):
        if not hasattr(self, '_ancestors_cache'):
            self._ancestors_cache = []
            if self.parent:
                self._ancestors_cache = list(self.parent.get_ancestors(include_self=True))
        return self._ancestors_cache

    def make_path(self, items):

        def join_path(joiner, field, ancestors):
            return joiner.join([force_unicode(getattr(i, field)) for i in ancestors])

        self.path = join_path(u'/', 'slug', items)
        path_max_length = self._meta.get_field('path').max_length
        if len(self.path) > path_max_length:
            slug_max_length = self._meta.get_field('slug').max_length
            short_path = self.path[:path_max_length - slug_max_length - 1]
            self.path = u'/'.join([short_path.rstrip(u'/'), get_unique_slug(self.slug, self.id)])

    def clean(self, *args, **kwargs):
        model_class = self.__class__
        try:
            original = model_class._default_manager.get(pk=self.pk)
        except model_class.DoesNotExist:
            original = None
        if self.system_flags:
            if not original is None:
                if self.system_flags.change_slug_restriction and original.slug != self.slug:
                    raise ValidationError(self.system_flags.get_label('change_slug_restriction'))
                if self.system_flags.change_parent_restriction and original.parent_id != self.parent_id:
                    raise ValidationError(self.system_flags.get_label('change_parent_restriction'))
        if not self.parent_id is None and self.parent.system_flags.has_child_restriction:
            if original is None or original.parent_id != self.parent_id:
                raise ValidationError(self.system_flags.get_label('has_child_restriction'))
        return super(BaseRubric, self).clean(*args, **kwargs)

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if not force_update:
            model_class = self.__class__
            ancestors = self.get_ancestors_list()
            try:
                original = model_class._default_manager.get(pk=self.pk)
                if original.active != self.active:
                    update_id_list = [x.id for x in self.get_descendants(include_self=False)]
                    if self.active:
                        update_id_list.extend([x.id for x in self.get_ancestors_list()])
                    self.get_base_instance_class()._default_manager.filter(id__in=update_id_list).update(active=self.active)
            except model_class.DoesNotExist:
                pass
            self.tags = ' '.join([tag.lower() for tag in self.tags.split()]) if self.tags else None
            self.make_path(ancestors + [self,])
            try:
                result = super(BaseRubric, self).save(force_insert, force_update, *args, **kwargs)
            except IntegrityError as e:
                if model_class._default_manager.exclude(pk=self.pk).filter(path=self.path).exists():
                    self.slug = get_unique_slug(self.slug, self.id)
                    self.make_path(ancestors + [self,])
                    result = super(BaseRubric, self).save(force_insert, force_update, *args, **kwargs)
                else:
                    raise e
        else:
            result = super(BaseRubric, self).save(force_insert, force_update, *args, **kwargs)
        return result

    def delete(self):
        if not self.system_flags.delete_restriction:
            super(BaseRubric, self).delete()

    def hard_delete(self):
        super(BaseRubric, self).delete()

    def move_to(self, target, position='first-child'):
        if position in ('left', 'right'):
            if self.system_flags.change_parent_restriction and target.parent_id != self.parent_id:
                raise InvalidMove(self.system_flags.get_label('change_parent_restriction'))
            if not target.parent_id is None and target.parent.system_flags.has_child_restriction and target.parent_id != self.parent_id:
                raise InvalidMove(self.system_flags.get_label('has_child_restriction'))
        elif position in ('first-child', 'last-child'):
            if target.id != self.parent_id:
                if self.system_flags.change_parent_restriction:
                    raise InvalidMove(self.system_flags.get_label('change_parent_restriction'))
                if target.system_flags.has_child_restriction:
                    raise InvalidMove(self.system_flags.get_label('has_child_restriction'))
        super(BaseRubric, self).move_to(target, position)

    def get_classification_method(self):
        return self.get_real_instance_class().CLASSIFICATION_METHOD[0]

    def get_classification_method_display(self):
        return self.get_real_instance_class().CLASSIFICATION_METHOD[1]
    get_classification_method_display.short_description = _('classification method')

    def _get_cached_get_active_children(self):
        key = BaseRubric.RUBRIC_ACTIVE_CHILDREN_CACHE_KEY_PATTERN % {'id': self.id}
        children = cache.get(key, None)
        if children is None:
            children = list(self.get_children().filter(active=True))
            cache.set(key, children, BaseRubric.CACHE_TIMEOUT)
        return children

    def get_active_children(self):
        if not hasattr(self, '_BaseRubric__active_children_cache'):
            self.__active_children_cache = self._get_cached_get_active_children()
        return self.__active_children_cache

    def get_all_active_characteristics_descendants_ids(self):
        key = BaseRubric.RUBRIC_CHARACTERISTIC_DESCENDANTS_IDS_CACHE_KEY
        descendants_ids = cache.get(key, None)
        if descendants_ids is None:
            Model = self.get_base_instance_class()
            characteristics_queryset = Model.objects.active().filter(attribute_mode=Model.ATTRIBUTE_IS_CHARACTERISTIC)
            if characteristics_queryset:
                descendants_ids = list(get_queryset_descendants(
                    characteristics_queryset).active().order_by().values_list('id', flat=True).distinct())
            else:
                descendants_ids = []
            cache.set(key, descendants_ids, BaseRubric.CACHE_TIMEOUT)
        return descendants_ids

    def get_all_active_marks_descendants_ids(self):
        key = BaseRubric.RUBRIC_MARK_DESCENDANTS_IDS_CACHE_KEY
        descendants_ids = cache.get(key, None)
        if descendants_ids is None:
            Model = self.get_base_instance_class()
            marks_queryset = Model.objects.active().filter(attribute_mode=Model.ATTRIBUTE_IS_MARK)
            if marks_queryset:
                descendants_ids = list(get_queryset_descendants(
                    marks_queryset).active().order_by().values_list('id', flat=True).distinct())
            else:
                descendants_ids = []
            cache.set(key, descendants_ids, BaseRubric.CACHE_TIMEOUT)
        return descendants_ids

    def get_image(self):
        return None

    @models.permalink
    def get_absolute_endpoint_url(self):
        return ('rubric_list', ())

    @models.permalink
    def get_absolute_url(self):
        return ('rubric_detail', (), {'pk': self.pk})

    def get_name(self):
        return self.name


#==============================================================================
# Facet
#==============================================================================
FACET_CLASSIFICATION = 'facet'
class FacetMixIn(object):

    CLASSIFICATION_METHOD = (FACET_CLASSIFICATION, _('facet'))


#==============================================================================
# Hierarchy
#==============================================================================
HIERARCHY_CLASSIFICATION = 'hierarchy'
class HierarchyMixIn(object):

    CLASSIFICATION_METHOD = (HIERARCHY_CLASSIFICATION, _('hierarchy'))


#==============================================================================
# Determinant
#==============================================================================
DETERMINANT_CLASSIFICATION = 'determinant'
class DeterminantMixIn(object):

    CLASSIFICATION_METHOD = (DETERMINANT_CLASSIFICATION, _('determinant'))


#==============================================================================
# RubricInfo & TreeInfo
#==============================================================================
class TreeInfo(dict):
    def __init__(self, root=None, *args, **kwargs):
        self.root = root
        super(TreeInfo, self).__init__(*args, **kwargs)

    def get_hash(self):
        keys = [x.rubric.id for x in self.values() if x.is_leaf]
        return hash_unsorted_list(keys) if keys else ''

    def trim(self, ids=None):
        tree = self.deepcopy()
        tree._expand()
        return tree._trim(ids)

    def _expand(self):
        rubrics = [x.rubric for x in self.values() if x.is_leaf]
        if rubrics:
            for rubric in get_queryset_descendants(rubrics, include_self=False).filter(active=True):
                ancestor = self.get(rubric.parent_id)
                child = self[rubric.id] = RubricInfo(rubric=rubric, is_leaf=True)
                ancestor.is_leaf = False
                ancestor.append(child)

    def _trim(self, ids=None):
        if ids is None:
            ids = []
        #ids = uniq(ids)
        root_model_class = self.root.rubric.__class__
        root = RubricInfo(rubric=root_model_class())
        tree = TreeInfo(root)
        for id in ids:
            src_node = self.get(id)
            if not src_node is None:
                if not id in tree:
                    node = tree[id] = RubricInfo(rubric=src_node.rubric, is_leaf=True)
                    src_ancestor = self.get(node.rubric.parent_id)
                    while src_ancestor:
                        ancestor = tree.get(src_ancestor.rubric.id)
                        if not ancestor:
                            node = tree[src_ancestor.rubric.id] = RubricInfo(rubric=src_ancestor.rubric, is_leaf=False, children=[node])
                            if node.rubric.parent_id is None:
                                root.append(node)
                                break
                        else:
                            ancestor.is_leaf = False
                            ancestor.append(node)
                            break
                        src_ancestor = self.get(src_ancestor.rubric.parent_id)
                    else:
                        root.append(node)
        for ancestor in [x for x in tree.values() if x.is_leaf]:
            src_ancestor = self[ancestor.rubric.id]
            if len(src_ancestor):
                ancestor.is_leaf = False
                for src_node in src_ancestor:
                    ancestor.append(tree._copy_recursively(src_node))
        return tree

    def _copy_recursively(self, src_node):
        node = self[src_node.rubric.id] = RubricInfo(rubric=src_node.rubric, is_leaf=src_node.is_leaf)
        for src_child in src_node:
            node.append(self._copy_recursively(src_child))
        return node

    def deepcopy(self):
        root_model_class = self.root.rubric.__class__
        root = RubricInfo(rubric=root_model_class())
        tree = TreeInfo(root)
        for src_node in self.root:
            root.append(tree._copy_recursively(src_node))
        return tree


class RubricInfo(list):

    CACHE_TIMEOUT = 3600

    DECOMPRESS_BUFFER_CACHE_KEY = 'dc_bf'
    DECOMPRESS_BUFFER_CACHE_SIZE = 500
    DECOMPRESS_TREE_CACHE_KEY_PATTERN = 'tr_i::%(model_name)s:%(value_hash)s:%(fix_it)s'

    def __init__(self, rubric=None, is_leaf=False, children=(), attrs=None):
        super(RubricInfo, self).__init__(children)
        self.attrs = attrs or {}
        self.rubric, self.is_leaf = rubric, is_leaf

    def get_children_dict(self):
        result = {}
        for child in self:
            result[child.rubric.id] = child
        return result

    def get_descendants_ids(self):
        result = []
        for child in self:
            result.append(child.rubric.id)
            result.extend(child.get_descendants_ids())
        return result

    @staticmethod
    def decompress(model_class, value=None, fix_it=False):
        if value is None:
            value = []
        value = uniq(value)
        root_model_class = get_base_polymorphic_model(model_class)
        root = RubricInfo(rubric=root_model_class())
        tree = TreeInfo(root)
        for rubric in model_class._default_manager.filter(pk__in=value).select_related('parent'):
            if not rubric.id in tree:
                node = tree[rubric.id] = RubricInfo(rubric=rubric, is_leaf=True)
                rubric_parent = rubric.parent
                if rubric_parent:
                    ancestor = tree.get(rubric_parent.id)
                    if not ancestor is None:
                        ancestor.is_leaf = False
                        ancestor.append(node)
                    else:
                        node = tree[rubric_parent.id] = RubricInfo(rubric=rubric_parent, is_leaf=False, children=[node])
                        if not rubric_parent.parent_id is None:
                            for rubric_ancestor in rubric_parent.get_ancestors(ascending=True).exclude(pk__in=tree.keys()):
                                node = tree[rubric_ancestor.id] = RubricInfo(rubric=rubric_ancestor, is_leaf=False, children=[node])
                            ancestor = tree.get(node.rubric.parent_id)
                            if not ancestor is None:
                                ancestor.is_leaf = False
                                ancestor.append(node)
                            else:
                                root.append(node)
                        else:
                            root.append(node)
                else:
                    root.append(node)
        if fix_it:
            invalid_ids = []
            for x in [x for x in tree.values() if not x.is_leaf]:
                if len(x) > 1 and (x.rubric.get_classification_method() == HIERARCHY_CLASSIFICATION):
                    invalid_ids.extend(x.get_descendants_ids())
                    x.is_leaf = True
                    del x[:]
            for id in invalid_ids:
                del tree[id]
        return tree

    @staticmethod
    def cached_decompress(model_class, value=None, fix_it=False):
        key = RubricInfo.DECOMPRESS_TREE_CACHE_KEY_PATTERN % {
            "model_name": model_class.__name__,
            "value_hash": hash_unsorted_list(value) if value else '',
            "fix_it": 'Y' if fix_it else 'N'
        }
        tree = cache.get(key, None)
        if tree is None:
            tree = RubricInfo.decompress(model_class, value, fix_it)
            cache.set(key, tree, RubricInfo.CACHE_TIMEOUT)
            buf = RubricInfo.get_decompress_buffer()
            old_key = buf.record(key)
            if not old_key is None:
                cache.delete(old_key)
        return tree

    @staticmethod
    def get_decompress_buffer():
        return RingBuffer.factory(RubricInfo.DECOMPRESS_BUFFER_CACHE_KEY,
                                  max_size=RubricInfo.DECOMPRESS_BUFFER_CACHE_SIZE, empty=None)

    @staticmethod
    def clear_decompress_buffer():
        buf = RubricInfo.get_decompress_buffer()
        keys = buf.get_all()
        buf.clear()
        cache.delete_many(keys)


#==============================================================================
# FacetFilteringMixin
#==============================================================================
class FacetFilteringMixin(object):

    def make_filters(self, *args, **kwargs):
        rubric_info = kwargs.pop('rubric_info')
        field_name = kwargs.get('field_name')
        filters = filter(None, (x.rubric.get_real_instance().make_filters(rubric_info=x, *args, **kwargs) for x in rubric_info))
        if rubric_info.is_leaf or not filters:
            if self.pk is not None:
                id_list = [x.pk for x in self.get_descendants(include_self=True).filter(active=True)]
                result = [models.Q(**{field_name + '__in': id_list})] if len(id_list) > 1 else [models.Q(**{field_name: id_list[0]})]
            else:
                result = []
        else:
            result = filters[0]
            for z in filters[1:]:
                r = []
                for x in result:
                    for y in z:
                        r.append(x | y)
                result = r
            if self.pk is not None:
                result = [models.Q(**{field_name: self.pk}) | x for x in result]
        return result


#==============================================================================
# DeterminantFilteringMixin
#==============================================================================
class DeterminantFilteringMixin(object):

    def make_filters(self, *args, **kwargs):
        rubric_info = kwargs.pop('rubric_info')
        field_name = kwargs.get('field_name')
        filters = filter(None, (x.rubric.get_real_instance().make_filters(rubric_info=x, *args, **kwargs) for x in rubric_info if not x.is_leaf))
        if rubric_info.is_leaf or not filters:
            if self.pk is not None:
                id_list = [x.pk for x in self.get_descendants(include_self=True).filter(active=True)]
                result = [models.Q(**{field_name + '__in': id_list})] if len(id_list) > 1 else [models.Q(**{field_name: id_list[0]})]
            else:
                result = []
        else:
            result = []
            for x in filters:
                for y in x:
                    result.append(y)
        return result
