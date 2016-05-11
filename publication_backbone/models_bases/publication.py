# -*- coding: utf-8 -*-
from datetime import datetime
from functools import wraps

import django
from django.db import models, transaction
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.html import escape
from django.utils import six
from django.core.urlresolvers import reverse
from django.core.cache import cache

from mptt.fields import TreeManyToManyField, TreeForeignKey
from polymorphic.polymorphic_model import PolymorphicModel
from sorl.thumbnail import ImageField

from publication_backbone.models_bases.mixins import PolymorphicModelMixin, PlaceholderImageMixin
from publication_backbone.models_bases.rubricator import RubricInfo
from publication_backbone.models import Rubric, Category, Facet

from publication_backbone.utils.circular_buffer_in_cache import RingBuffer
from publication_backbone.utils.loader import get_publication_backbone_model_string
from publication_backbone.utils.media import get_media_path
from publication_backbone.utils.contrib import create_uid, uniq

from fluent_contents.models.fields import PlaceholderField
from fluent_contents.models import ContentItemRelation, PlaceholderRelation		



def on_publication_group_delete(collector, field, sub_objs, using):

    def set_grp(objs, using):
        for obj in objs:
            obj.set_grp()
            obj.save(force_update=True, using=using)

    def update_publications(objs, func):

        @wraps(func)
        def decorated(*args, **kwargs):
            res = func(*args, **kwargs)
            if django.VERSION >= (1, 6):
                with transaction.atomic(using):
                    set_grp(objs, using)
            else:
                with transaction.commit_on_success(using):
                    set_grp(objs, using)
            return res
        return decorated

    collector.delete = update_publications(sub_objs, collector.delete)
    collector.add_field_update(field, None, sub_objs)


#==============================================================================
# BasePublication & PublicationCharacteristicOrMarkInfo & PublicationCharacteristicOrMarkSet Cache system
#==============================================================================
class PublicationCharacteristicOrMarkInfo(object):

    def __init__(self, name, path, values, tags, tree_id, tree_left):
        self.id = id
        self.name = name
        self.path = path
        self.values = values
        self.tags = tags
        self.tree_id = tree_id
        self.tree_left = tree_left

    def __cmp__(self, other):
        if self.tree_id == other.tree_id:
            if self.tree_left == other.tree_left:
                return 0
            elif self.tree_left < other.tree_left:
                return -1
            else:
                return 1
        elif self.tree_id < other.tree_id:
            return -1
        else:
            return 1

    def __repr__(self):
        return repr((self.name, self.values))


class PublicationCharacteristicOrMarkSet(object):
    """
    Represents a lazy database lookup for a set of attributes.
    """

    def __init__(self, rubrics, additional_characteristics_or_marks, attribute_mode, tree_opts):
        self.rubrics = rubrics
        self.additional_characteristics_or_marks = additional_characteristics_or_marks
        self.attribute_mode = attribute_mode
        self.tree_opts = tree_opts
        self._result_cache = {}

    def all(self, limit=None):
        if not limit in self._result_cache:
            result = self._get_attributes(limit)
            self._result_cache[limit] = result
        else:
            result = self._result_cache[limit]
        return result

    def __getitem__(self, k):
        """
        Retrieves an item or slice from the set of results.
        """
        if not isinstance(k, (slice,) + six.integer_types):
            raise TypeError
        assert ((not isinstance(k, slice) and (k >= 0)) or
                (isinstance(k, slice) and (k.start is None or k.start >= 0) and
                 (k.stop is None or k.stop >= 0))), \
            "Negative indexing is not supported."
        limit = None
        if isinstance(k, slice):
            if k.stop is not None:
                limit = int(k.stop)
        return self.all(limit)[k]

    @staticmethod
    def _get_attr_ancs_by_rbrc(rubric, attribute_mode):
        key = Rubric.RUBRIC_ATTRIBUTES_ANCESTORS_CACHE_KEY_PATTERN % {'id': rubric.id, 'attribute_mode': attribute_mode}
        ancestors = cache.get(key, None)
        if ancestors is None:
            ancestors = list(rubric.get_ancestors(ascending=True, include_self=False).filter(attribute_mode=attribute_mode).select_related('parent'))
            cache.set(key, ancestors, Rubric.CACHE_TIMEOUT)
        return ancestors

    def _get_attributes(self, limit=None):
        """
        Return attributes objects of publication
        """
        attrs0 = []
        cnt = 0
        seen_attrs = {}
        for rubric in self.rubrics:
            if limit and cnt > limit:
                break
            ancestors = PublicationCharacteristicOrMarkSet._get_attr_ancs_by_rbrc(rubric, self.attribute_mode)
            if ancestors:
                attr0 = ancestors.pop(0)
                prev_attr = attr0
                buffer = []
                for ancestor in ancestors:
                    index = seen_attrs.get(ancestor.id)
                    if index is None:
                        if prev_attr.parent_id != ancestor.id:
                            buffer.insert(0, {
                                'attr': ancestor,
                                'rubric': prev_attr.parent
                            })
                        prev_attr = ancestor
                    else:
                        if prev_attr.parent_id != ancestor.id:
                            attr_info = attrs0[index]
                            attr_info.values.append(prev_attr.parent.name)
                            if prev_attr.parent.tags:
                                attr_info.tags.extend(prev_attr.parent.tags.split())
                        break
                for obj in buffer:
                    attr = obj['attr']
                    seen_attrs[attr.id] = len(attrs0)
                    tags = attr.tags.split() if attr.tags else []
                    if obj['rubric'].tags:
                        tags.extend(obj['rubric'].tags.split())
                    attrs0.append(PublicationCharacteristicOrMarkInfo(attr.name, attr.path, [obj['rubric'].name],
                                                       tags,
                                                       getattr(attr, self.tree_opts.tree_id_attr),
                                                       getattr(attr, self.tree_opts.left_attr)))
                    cnt += 1
                if rubric.attribute_mode != self.attribute_mode:
                    index = seen_attrs.get(attr0.id)
                    if index is None:
                        seen_attrs[attr0.id] = len(attrs0)
                        tags = attr0.tags.split() if attr0.tags else []
                        if rubric.tags:
                            tags.extend(rubric.tags.split())
                        attrs0.append(PublicationCharacteristicOrMarkInfo(attr0.name, attr0.path, [rubric.name],
                                                           tags,
                                                           getattr(attr0, self.tree_opts.tree_id_attr),
                                                           getattr(attr0, self.tree_opts.left_attr)))
                        cnt += 1
                    else:
                        attr_info = attrs0[index]
                        attr_info.values.append(rubric.name)
                        if rubric.tags:
                            attr_info.tags.extend(rubric.tags.split())
        attrs1 = []
        prev_id = None
        cnt = 0
        for additional_attribute in self.additional_characteristics_or_marks.select_related('rubric'):
            if limit and cnt > limit:
                break
            attribute = additional_attribute.rubric
            if attribute.id != prev_id:
                tags = attribute.tags.split() if attribute.tags else []
                if additional_attribute.tags:
                    tags.extend(additional_attribute.tags.split())
                attrs1.append(PublicationCharacteristicOrMarkInfo(attribute.name, attribute.path, [additional_attribute.value],
                                                   tags,
                                                   getattr(attribute, self.tree_opts.tree_id_attr),
                                                   getattr(attribute, self.tree_opts.left_attr)))
                cnt += 1
                prev_id = attribute.id
            else:
                attr_info = attrs1[-1]
                attr_info.values.append(additional_attribute.value)
                if additional_attribute.tags:
                    attr_info.tags.extend(additional_attribute.tags.split())
        # merge attributes
        attrs = []
        while attrs0 and attrs1:
            if attrs0[0] == attrs1[0]:
                attrs.append(attrs1.pop(0))
                attrs0.pop(0)
            elif attrs0[0] < attrs1[0]:
                attrs.append(attrs0.pop(0))
            else:
                attrs.append(attrs1.pop(0))
        if attrs0:
            attrs.extend(attrs0)
        elif attrs1:
            attrs.extend(attrs1)

        # clean not uniq values and tags
        for attr in attrs:
            if len(attr.values) > 1:
                attr.values = uniq(attr.values)
            if len(attr.tags) > 1:
                attr.tags = uniq(attr.tags)

        # sort values
        for attr in attrs:
            for v in attr.values:
                if not v.isdigit():
                    attr.values.sort()
                    break
            else:
                attr.values.sort(key=int)
        return attrs if limit is None else attrs[:limit]


class BasePublication(PlaceholderImageMixin, PolymorphicModelMixin, PolymorphicModel):
    """
    A basic Publication for the representing an Publication.
    """
    SPLIT_TAGS_CHARSET = ";"
    STRING_TAGS_CHARSET = ", "

    CACHE_TIMEOUT = 3600

    ADDED_YEAR = ('added-year', _('added year'))
    ADDED_YEAR_KEY = 'added-year-%s'
    ADDED_YEARS_CACHE_KEY = 'add_year::%(id)s' % {'id': create_uid()}
    ADDED_MONTH = ('added-month', _('added month'))
    ADDED_MONTH_KEY = 'added-month-%02d'
    ADDED_MONTHS_CACHE_KEY = 'add_month::%(id)s' % {'id': create_uid()}
    ADDED_DAY = ('added-day', _('added day'))
    ADDED_DAY_KEY = 'added-day-%02d'
    ADDED_DAY_RANGE_KEY = 'added-day-%02d-%02d'
    ADDED_DAYS_CACHE_KEY = 'add_day::%(id)s' % {'id': create_uid()}

    POTENTIAL_RUBRICS_BUFFER_CACHE_KEY = 'ptntl_bf'
    POTENTIAL_RUBRICS_BUFFER_CACHE_SIZE = 500
    POTENTIAL_RUBRICS_IDS_CACHE_KEY_PATTERN = 'ptntl_rd::%(tree_hash)s'

    REAL_RUBRICS_BUFFER_CACHE_KEY = 'rl_bf'
    REAL_RUBRICS_BUFFER_CACHE_SIZE = 500
    REAL_RUBRICS_IDS_CACHE_KEY_PATTERN = 'rl_rd::%(tree_hash)s'

    name = models.CharField(max_length=255, verbose_name=_('name'))
    sub_name = models.CharField(max_length=600, verbose_name=_('sub name'), null=True, blank=True)
    slug = models.SlugField(verbose_name=_('slug'), unique=True, help_text=_("For use into URL"))
    author = models.CharField(verbose_name=_('author'), null=True, blank=True, max_length=255)
    description = models.TextField(verbose_name=_('lead'), null=True, blank=True)
    tags = models.CharField(verbose_name=_('tags'), help_text=_('use semicolon as tag divider'), blank=True, max_length=255)
    active = models.BooleanField(default=False, verbose_name=_('active'), help_text=_("If this flag disable the publication not show anywhere"))

    comments_enabled = models.BooleanField(default=False, verbose_name=_('Comments enabled'))
    is_main = models.BooleanField(default=False, verbose_name=_('Main material'))

    group = models.ForeignKey(get_publication_backbone_model_string('PublicationGroup'), related_name='publications',
                              blank=True, null=True, on_delete=on_publication_group_delete, verbose_name=_('group')) #models.SET_NULL
    grp = models.CharField(verbose_name=_("coalesce group id"), max_length=255, db_index=True, editable=False)

    content = PlaceholderField("publication_content", verbose_name=_("Content"))

    date_added = models.DateTimeField(default=datetime.now,
        verbose_name=_('date added'))

    show_date = models.BooleanField(default=True, verbose_name=_('Show date'), help_text=_("Show date"))

    last_modified = models.DateTimeField(auto_now=True,
        verbose_name=_('last modified'))

    rubrics = TreeManyToManyField(
        get_publication_backbone_model_string('Rubric'),
        related_name='catalog_items',
        verbose_name=_('rubrics'),
        blank=True)

    contentitem_set = ContentItemRelation()
    placeholder_set = PlaceholderRelation()
    
    class Meta:
        abstract = True
        app_label = 'publication'
        verbose_name = _('publication')
        verbose_name_plural = _('publication')

    def __unicode__(self):
        return self.name

    def set_grp(self):
        if self.group:
            self.grp = '1.%s' % self.group.pk
        else:
            self.grp = '0.%s' % (self.pk if self.pk else create_uid())

    def get_tags(self):
        str_tags = self.tags.replace(self.SPLIT_TAGS_CHARSET, self.STRING_TAGS_CHARSET)
        return str_tags

    @staticmethod
    def get_added_years(year=None):
        year_key = BasePublication.ADDED_YEAR_KEY % year if not year is None else None
        key = BasePublication.ADDED_YEARS_CACHE_KEY
        added_years = cache.get(key, None)
        if added_years is None or not (year_key is None or year_key in added_years):
            added_years = {}
            try:
                added_year = Rubric.objects.get(slug=BasePublication.ADDED_YEAR[0])
                for rubric in added_year.get_descendants(include_self=False):
                    added_years[rubric.slug] = rubric
            except Rubric.DoesNotExist:
                added_year = None
            if added_year and not (year_key is None or year_key in added_years):
                rubric = Facet(slug=year_key,
                             name="%s" % year,
                             parent=added_year,
                             system_flags=Rubric.system_flags.delete_restriction | \
                                Rubric.system_flags.change_parent_restriction | \
                                Rubric.system_flags.change_slug_restriction | \
                                Rubric.system_flags.change_subclass_restriction | \
                                Rubric.system_flags.has_child_restriction | \
                                Rubric.system_flags.tagged_restriction)
                rubric.save()
                added_years[rubric.slug] = rubric
            cache.set(key, added_years, None)
        return added_years

    @staticmethod
    def get_added_months():
        key = BasePublication.ADDED_MONTHS_CACHE_KEY
        added_months = cache.get(key, None)
        if added_months is None:
            added_months = {}
            try:
                added_month = Rubric.objects.get(slug=BasePublication.ADDED_MONTH[0])
                for rubric in added_month.get_descendants(include_self=False):
                    added_months[rubric.slug] = rubric
            except Rubric.DoesNotExist:
                pass
            cache.set(key, added_months, None)
        return added_months

    @staticmethod
    def get_added_days():
        key = BasePublication.ADDED_DAYS_CACHE_KEY
        added_days = cache.get(key, None)
        if added_days is None:
            added_days = {}
            try:
                added_day = Rubric.objects.get(slug=BasePublication.ADDED_DAY[0])
                for rubric in added_day.get_descendants(include_self=False):
                    added_days[rubric.slug] = rubric
            except Rubric.DoesNotExist:
                pass
            cache.set(key, added_days, None)
        return added_days

    def validate_rubrics(self, pk_set=None):
        if pk_set is None:
            pk_set = set(self.rubrics.values_list('id', flat=True))
        normal_pk_set = pk_set.copy()

        added_year = self.date_added.year
        year_key = BasePublication.ADDED_YEAR_KEY % added_year
        added_years = self.get_added_years(added_year)
        if bool(added_years):
            normal_pk_set = normal_pk_set - set([rubric.id for rubric in added_years.values()])
            normal_pk_set.add(added_years[year_key].id)

        month_key = BasePublication.ADDED_MONTH_KEY % self.date_added.month
        added_months = self.get_added_months()
        if bool(added_months):
            normal_pk_set = normal_pk_set - set([rubric.id for rubric in added_months.values()])
            normal_pk_set.add(added_months[month_key].id)

        day_key = BasePublication.ADDED_DAY_KEY % self.date_added.day
        added_days = self.get_added_days()
        if bool(added_days):
            normal_pk_set = normal_pk_set - set([rubric.id for rubric in added_days.values()])
            normal_pk_set.add(added_days[day_key].id)

        # normalize rubric set
        tree = RubricInfo.decompress(self._meta.get_field('rubrics').rel.to, normal_pk_set, fix_it=False)
        normal_pk_set = set([x.rubric.id for x in tree.values() if x.is_leaf])

        # try update rubric set
        if normal_pk_set != pk_set:
            self._during_rubrics_validation = True
            pk_set_difference = pk_set - normal_pk_set
            difference_list = list(pk_set_difference)
            self.rubrics.remove(*difference_list)
            pk_set_difference = normal_pk_set - pk_set
            difference_list = list(pk_set_difference)
            self.rubrics.add(*difference_list)
            del self._during_rubrics_validation

    def save(self, force_insert=False, force_update=False, force_validate_rubrics=False, *args, **kwargs):
        if not force_update:
            model_class = self.__class__
            try:
                original = model_class._default_manager.get(pk=self.pk)
                #validate_rubrics = self.in_stock != original.in_stock or self.get_price() != original.get_price()
                validate_rubrics = force_validate_rubrics or self.date_added != original.date_added
            except model_class.DoesNotExist:
                validate_rubrics = True
            self.set_grp()
        result = super(BasePublication, self).save(force_insert, force_update, *args, **kwargs)
        if not force_update and validate_rubrics:
            self.validate_rubrics()
        return result

    def get_name(self):
        """
        Return the name of current publication (base)
        """
        return self.name

    def get_author(self):
        """
        Return the author of current publication (base)
        """
        return self.author

    def get_sub_name(self):
        """
        Return the name of current publication (base)
        """
        return self.sub_name

    def get_publication_reference(self):
        """
        Return publication reference of current publication (base)
        """
        return unicode(self.pk)

    @staticmethod
    def get_pk_by_publication_reference(value):
        """
        Return pk by publication reference
        """
        return value


    def group_name(self):
        if self.group:
            app_label = self.group._meta.app_label
            admin_url = reverse('admin:%s_%s_change'
                            % (app_label, self.group._meta.object_name.lower()),
                            args=(self.group.id,), current_app=app_label)
            return mark_safe(u'<a href="%s">%s</a>' %
                         (admin_url,
                          escape(capfirst(self.group.get_name()))))
        return u""
    group_name.short_description = _('Group name')

    def get_image(self):
        """
        Return main image of current publication if exist
        """
        if not hasattr(self, '_BasePublication__image_cache'):
            images = self.get_images()
            self.__image_cache = images[0].picture if images else None
        return self.__image_cache

    def get_images(self):
        """
        Return all image objects of current publication
        """
        if not hasattr(self, '_BasePublication__images_cache'):
            self.__images_cache = self.images.all()
        return self.__images_cache

    def get_description(self):
        """
        Return text description of current publication
        """
        return self.description

    def get_characteristics(self):
        """
        Return all characteristics objects of current publication
        """
        if not hasattr(self, '_BasePublication__characteristics_cache'):
            tree_opts = Rubric._mptt_meta
            self.__characteristics_cache = PublicationCharacteristicOrMarkSet(
                self.get_active_rubrics_for_characteristics(),
                self.get_additional_characteristics(),
                Rubric.ATTRIBUTE_IS_CHARACTERISTIC,
                tree_opts)
        return self.__characteristics_cache

    def get_marks(self):
        """
        Return all attributes objects of current publication
        """
        if not hasattr(self, '_BasePublication__marks_cache'):
            tree_opts = Rubric._mptt_meta
            self.__marks_cache = PublicationCharacteristicOrMarkSet(
                self.get_active_rubrics_for_marks(),
                self.get_additional_marks(),
                Rubric.ATTRIBUTE_IS_MARK,
                tree_opts)
        return self.__marks_cache

    def get_active_rubrics_for_characteristics(self):
        """
        Return rubrics for characteristics of current publication
        """
        if not hasattr(self, '_BasePublication__active_rubrics_for_characteristics_cache'):
            tree_opts = Rubric._mptt_meta
            descendants_ids = Rubric().get_all_active_characteristics_descendants_ids()
            self.__active_rubrics_for_characteristics_cache = list(
                self.rubrics.filter(id__in=descendants_ids).order_by(tree_opts.tree_id_attr, tree_opts.left_attr))
        return self.__active_rubrics_for_characteristics_cache

    def get_active_rubrics_for_marks(self):
        """
        Return rubrics for marks of current publication
        """
        if not hasattr(self, '_BasePublication__active_rubrics_for_marks_cache'):
            tree_opts = Rubric._mptt_meta
            descendants_ids = Rubric().get_all_active_marks_descendants_ids()
            self.__active_rubrics_for_marks_cache = list(
                self.rubrics.filter(id__in=descendants_ids).order_by(tree_opts.tree_id_attr, tree_opts.left_attr))
        return self.__active_rubrics_for_marks_cache

    def get_additional_characteristics(self):
        """
        Return additional characteristics of current publication
        """
        if not hasattr(self, '_BasePublication__additional_characteristics_cache'):
            tree_opts = Rubric._mptt_meta
            self.__additional_characteristics_cache = self.additional_characteristics_or_marks.filter(
                rubric__attribute_mode=Rubric.ATTRIBUTE_IS_CHARACTERISTIC).\
                order_by('rubric__%s' % tree_opts.tree_id_attr, 'rubric__%s' % tree_opts.left_attr)
        return self.__additional_characteristics_cache

    def get_additional_marks(self):
        """
        Return additional marks of current publication
        """
        if not hasattr(self, '_BasePublication__additional_marks_cache'):
            tree_opts = Rubric._mptt_meta
            self.__additional_marks_cache = self.additional_characteristics_or_marks.filter(
                rubric__attribute_mode=Rubric.ATTRIBUTE_IS_MARK).\
                order_by('rubric__%s' % tree_opts.tree_id_attr, 'rubric__%s' % tree_opts.left_attr)
        return self.__additional_marks_cache

    def get_relations(self):
        """
        Return relations with other publications
        """
        if not hasattr(self, '_BasePublication__relations_cache'):
            tree_opts = Rubric._mptt_meta
            self.__relations_cache = self.forward_relations.select_related('rubric', 'to_publication').order_by(
                'rubric__%s' % tree_opts.tree_id_attr, 'rubric__%s' % tree_opts.left_attr)
        return self.__relations_cache

    def get_rubrics_count(self):
        """
        Return count of related rubrics with current publication
        """
        if not hasattr(self, '_BasePublication__rubrics_count_cache'):
            self.__rubrics_count_cache = self.rubrics.count()
        return self.__rubrics_count_cache
    get_rubrics_count.short_description = _('Number of rubrics')

    def get_rubrics_with_image(self):
        """
        Return all related rubrics with images of current publication
        """
        if not hasattr(self, '_BasePublication__rubrics_with_image_cache'):
            tree_opts = Rubric._mptt_meta
            rubrics = self.rubrics.order_by(tree_opts.tree_id_attr, tree_opts.left_attr)
            self.__rubrics_with_image_cache = [x for x in rubrics if x.get_image()]
        return self.__rubrics_with_image_cache

    def get_related_categories(self):
        """
        Return all related categories with current publication
        """
        if not hasattr(self, '_BasePublication__related_categories_cache'):
            self.__related_categories_cache = self.related_categories.select_related('category').all()
        return self.__related_categories_cache

    def get_related_by_tags_publications(self):
        return None

    def get_category(self):
        if not hasattr(self, '_BasePublication__category_cache'):
            publication_rubrics_ids = self.rubrics.active().values_list('id', flat=True)
            category = Category()
            all_publication_rubrics_ids = RubricInfo.decompress(Rubric, publication_rubrics_ids, fix_it=False).keys()
            all_category_rubrics_ids = category.get_all_category_active_rubrics_ids()
            crossing_rubrics_ids = list(set(all_publication_rubrics_ids) & set(all_category_rubrics_ids))
            tree_opts = Category._mptt_meta
            crossing_categories_info = Category.objects.distinct().filter(rubrics__id__in=crossing_rubrics_ids).\
                annotate(num=Count('rubrics__id')).values('id', 'num').\
                order_by('-num', '-' + tree_opts.level_attr, tree_opts.tree_id_attr, tree_opts.left_attr)
            all_categories_rubrics_count = category.get_all_category_active_rubrics_count()
            for obj in crossing_categories_info:
                id = obj['id']
                num = all_categories_rubrics_count.get(id)
                if not num is None and num == obj['num']:
                    self.__category_cache = Category.objects.get(id=id)
                    break
            else:
                self.__category_cache = None
        return self.__category_cache


    @models.permalink
    def get_absolute_endpoint_url(self):
        """
        Return url to publication list
        """
        return ('publication_list', ())

    @models.permalink
    def get_absolute_url(self):
        """
        Return url to current publication detail
        """
        return ('publication_detail', (), {'slug': self.slug})

    @staticmethod
    def get_potential_rubrics_buffer():
        return RingBuffer.factory(BasePublication.POTENTIAL_RUBRICS_BUFFER_CACHE_KEY, max_size=BasePublication.POTENTIAL_RUBRICS_BUFFER_CACHE_SIZE, empty=None)

    @staticmethod
    def get_real_rubrics_buffer():
        return RingBuffer.factory(BasePublication.REAL_RUBRICS_BUFFER_CACHE_KEY, max_size=BasePublication.REAL_RUBRICS_BUFFER_CACHE_SIZE, empty=None)

    @staticmethod
    def clear_potential_rubrics_buffer():
        buf = BasePublication.get_potential_rubrics_buffer()
        keys = buf.get_all()
        buf.clear()
        cache.delete_many(keys)

    @staticmethod
    def clear_real_rubrics_buffer():
        buf = BasePublication.get_real_rubrics_buffer()
        keys = buf.get_all()
        buf.clear()
        cache.delete_many(keys)

    @staticmethod
    def try_format_values_query_set(queryset):
        return queryset.model.objects.from_values_query_set(queryset)


#==============================================================================
# BasePublicationImage
#==============================================================================
class BasePublicationImage(models.Model):
    """
    A picture of an item. Can have many pictures associated with an item.
    """
    publication = models.ForeignKey(get_publication_backbone_model_string('Publication'), related_name='images')
    picture = ImageField(verbose_name=_('Picture'), upload_to=get_media_path, max_length=200)
    caption = models.CharField(_("Optional caption"), max_length=100, null=True, blank=True)
    sort = models.IntegerField(_("Sort Order"), default=0)

    def __unicode__(self):
        if self.caption:
            return _(u"%s") % self.caption[:40]

        return _(u"%s") % self.picture

    class Meta:
        abstract = True


#==============================================================================
# BasePublicationRelatedCategory
#==============================================================================
class BasePublicationRelatedCategory(models.Model):
    """
    Related publication Category
    """
    publication = models.ForeignKey(get_publication_backbone_model_string('Publication'), related_name='related_categories')
    category = TreeForeignKey(get_publication_backbone_model_string('Category'), verbose_name=_('category'), related_name='+')

    class Meta:
        abstract = True

    def _name(self):
        return self.category.name
    name = property(_name)

    def __unicode__(self):
        return self.name


#==============================================================================
# BaseCategorypublicationRelation
#==============================================================================
class BaseCategoryPublicationRelation(models.Model):
    """
    Category publication Relation
    """
    RELATION_BIDIRECTIONAL = "b"
    RELATION_FORWARD = "f"
    RELATION_REVERSE = "r"

    RELATION_DIRECTIONS = (
        (RELATION_BIDIRECTIONAL, _('bidirectional')),
        (RELATION_FORWARD, _('forward')),
        (RELATION_REVERSE, _('reverse')),
    )

    category = TreeForeignKey(get_publication_backbone_model_string('Category'), verbose_name=_('category'), related_name='publication_relations')
    rubric = TreeForeignKey(get_publication_backbone_model_string('Rubric'), verbose_name=_('relation'), related_name='+',
                            help_text=_('Defines the relation using for filtering'))
    relation_direction = models.CharField(_("relation direction"), max_length=1,
                                          choices=RELATION_DIRECTIONS, default=RELATION_BIDIRECTIONAL,
                                          help_text=_('Defines the direction of relation on which selection is carried out'))

    class Meta:
        abstract = True

    def _name(self):
        return self.rubric.name
    name = property(_name)

    def __unicode__(self):
        return self.name


#==============================================================================
# BaseAdditionalPublicationCharacteristicOrMark
#==============================================================================
class BaseAdditionalPublicationCharacteristicOrMark(models.Model):
    """
    Allows arbitrary name/value pairs (as strings) to be attached to a publication.
    This is a simple way to add extra text or numeric info to a publication.
    If you want more structure than this, create your own subtype to add
    whatever you want to your Publications.
    """
    publication = models.ForeignKey(get_publication_backbone_model_string('Publication'), #null=True, blank=True,
                                related_name='additional_characteristics_or_marks', verbose_name=_('publication'))
    rubric = TreeForeignKey(get_publication_backbone_model_string('Rubric'), verbose_name=_('rubric'),
                               related_name='publication_additional_characteristics_or_marks', db_index=True)
    value = models.CharField(_("value"), max_length=255)
    tags = models.CharField(verbose_name=_('tags'), max_length=255, null=True, blank=True,
                            help_text=_('Space delimited tags, for example: "red strikethrough"'))

    class Meta:
        abstract = True
        verbose_name = _("additional publ. chars or mark")
        verbose_name_plural = _("additional publ. chars or marks")

    def _name(self):
        return u"%s: %s" % (self.rubric.name, self.value)
    name = property(_name)

    def __unicode__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if not force_update:
            self.tags = ' '.join([tag.lower() for tag in self.tags.split()]) if self.tags else None
        return super(BaseAdditionalPublicationCharacteristicOrMark, self).save(force_insert, force_update, *args, **kwargs)


#==============================================================================
# BasePublicationRelation
#==============================================================================
class BasePublicationRelation(models.Model):
    """
    Allows to be attached related publications.
    """
    from_publication = models.ForeignKey(get_publication_backbone_model_string('Publication'),
                                related_name='forward_relations', verbose_name=_('from publication'))

    to_publication = models.ForeignKey(get_publication_backbone_model_string('Publication'),
                                related_name='backward_relations', verbose_name=_('to publication'))

    rubric = TreeForeignKey(get_publication_backbone_model_string('Rubric'), verbose_name=_('rubric'),
                               related_name='+', db_index=True)

    class Meta:
        abstract = True
        verbose_name = _("publication relation")
        verbose_name_plural = _("publication relations")

    def _name(self):
        return u"%s: %s" % (self.rubric.name, self.to_publication.name)
    name = property(_name)

    def __unicode__(self):
        return self.name