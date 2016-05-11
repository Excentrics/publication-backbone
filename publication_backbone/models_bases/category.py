# -*- coding: utf-8 -*-
import datetime

from django.db import models

from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode

from mptt.fields import TreeManyToManyField

from publication_backbone.models_bases.modelmixins import ModelMixin
from publication_backbone.models_bases.rubricator import RubricInfo
from publication_backbone.models_bases.polymorphic_mptt.models import PolymorphicMPTTModel, PolymorphicTreeForeignKey
from publication_backbone.utils.loader import get_publication_backbone_model_string
from publication_backbone.utils.contrib import get_unique_slug
from publication_backbone.utils.validators import URLOrAbsolutePathValidator

from django.core.cache import cache


"""
#---------------------------------
import logging
from django.conf import settings
logger = logging.getLogger(settings.PROJECT_NAME)
#---------------------------------
"""

#==============================================================================
# Category
#==============================================================================
class AbstractBaseCategory(PolymorphicMPTTModel):
    """
    A model representing an Category.
    """
    CACHE_TIMEOUT = 3600
    CATEGORY_VISIBLE_CHILDREN_CACHE_KEY_PATTERN = 'ctgr_chldrn::%(id)d'

    parent = PolymorphicTreeForeignKey('self', verbose_name=_('parent'), null=True, blank=True, related_name='children',
                            db_index=True)
    name = models.CharField(verbose_name=_('name'), max_length=255)

    description = models.TextField(verbose_name=_('description'), null=True, blank=True)
    slug = models.SlugField(_("slug"), help_text=_("Used for URLs, auto-generated from name if blank"))
    creation_date = models.DateTimeField(verbose_name=_('creation date'), db_index=True, default=datetime.datetime.now,
                                         editable=False)
    visible = models.BooleanField(verbose_name=_('visible'), default=False, db_index=True)
    path = models.CharField(verbose_name=_("path"), max_length=255, db_index=True, editable=False,
                            unique=True)

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

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if not force_update:
            model_class = self.__class__
            ancestors = self.get_ancestors_list()
            try:
                original = model_class._default_manager.get(pk=self.pk)
                if original.visible != self.visible:
                    update_id_list = [x.id for x in self.get_descendants(include_self=False)]
                    if self.visible:
                        update_id_list.extend([x.id for x in ancestors])
                    self.get_base_instance_class()._default_manager.filter(id__in=update_id_list).update(visible=self.visible)
            except model_class.DoesNotExist:
                pass
            self.make_path(ancestors + [self,])

        result = super(AbstractBaseCategory, self).save(force_insert, force_update, *args, **kwargs)

        return result

    def _get_cached_get_visible_children(self):
        key = AbstractBaseCategory.CATEGORY_VISIBLE_CHILDREN_CACHE_KEY_PATTERN % {'id': self.id}
        children = cache.get(key, None)
        if children is None:
            children = list(self.get_children().filter(visible=True))
            cache.set(key, children, AbstractBaseCategory.CACHE_TIMEOUT)
        return children

    def get_visible_children(self):
        return self._get_cached_get_visible_children()

    @models.permalink
    def get_absolute_endpoint_url(self):
        return ('category_list', ())

    @models.permalink
    def get_absolute_url(self):
        return ('category_detail', (), {'pk': self.pk})

    def get_name(self):
        return self.name


#==============================================================================
# Rubric MixIn
#==============================================================================
class RubricMixIn(ModelMixin):

    CATEGORY_ACTIVE_RUBRIC_COUNT_CACHE_KEY = 'ctgr_act_rbrc_cnt'
    CATEGORY_ACTIVE_RUBRIC_IDS_CACHE_KEY = 'ctgr_act_rbrc_ids'

    rubrics = TreeManyToManyField(get_publication_backbone_model_string('Rubric'), verbose_name=_('rubrics'), blank=True)

    def validate_rubrics(self, pk_set=None):
        if pk_set is None:
            pk_set = set(self.rubrics.values_list('id', flat=True))
        normal_pk_set = pk_set.copy()

        tree = RubricInfo.decompress(self._meta.get_field('rubrics').rel.to, normal_pk_set, fix_it=True)
        normal_pk_set = set([x.rubric.id for x in tree.values() if x.is_leaf])

        if normal_pk_set != pk_set:
            self._during_rubrics_validation = True
            pk_set_difference = pk_set - normal_pk_set
            difference_list = list(pk_set_difference)
            self.rubrics.remove(*difference_list)
            pk_set_difference = normal_pk_set - pk_set
            difference_list = list(pk_set_difference)
            self.rubrics.add(*difference_list)
            del self._during_rubrics_validation

    def get_all_category_active_rubrics_count(self):
        key = self.CATEGORY_ACTIVE_RUBRIC_COUNT_CACHE_KEY
        result = cache.get(key, None)
        if result is None:
            category_rubrics_info = self.__class__.objects.distinct().filter(rubrics__active=True).annotate(
                num=models.Count('rubrics__id')).values('id', 'num')
            result = {}
            for obj in category_rubrics_info:
                result[obj['id']] = obj['num']
            cache.set(key, result, self.CACHE_TIMEOUT)
        return result

    def get_all_category_active_rubrics_ids(self):
        key = self.CATEGORY_ACTIVE_RUBRIC_IDS_CACHE_KEY
        result = cache.get(key, None)
        if result is None:
            category_rubrics_ids = self.__class__.rubrics.through.objects.distinct().filter(rubric__active=True).values_list('rubric__id', flat=True)
            result = RubricInfo.decompress(self.__class__.rubrics.field.rel.to, category_rubrics_ids, fix_it=False).keys()
            cache.set(key, result, self.CACHE_TIMEOUT)
        return result

    def get_active_rubrics_ids(self):
        if not hasattr(self, '_RubricMixIn__active_rubrics_ids_cache'):
            self.__active_rubrics_ids_cache = self.rubrics.active().values_list('id', flat=True)
        return self.__active_rubrics_ids_cache

    def get_catalog_items(self, use_cached_decompress=True, meta=None):
        rubric_model = self.__class__.rubrics.field.rel.to
        catalog_item_model = rubric_model.catalog_items.related.model
        queryset = catalog_item_model.objects.make_filtering(self.get_active_rubrics_ids(),
                                                             use_cached_decompress=use_cached_decompress, meta=meta)
        return queryset

    @models.permalink
    def get_catalog_url(self):
        return ('publication_list', (), {'path': self.path})


#==============================================================================
# Link MixIn
#==============================================================================
class LinkMixIn(ModelMixin):
    #url = models.URLField(verbose_name=_('URL'), max_length=200, help_text=_('Universal Resource Locator'))

    url = models.CharField(verbose_name=_('URL'), max_length=200, help_text=_('Universal Resource Locator'),
                           validators=[URLOrAbsolutePathValidator()])

    def get_url(self):
        return self.url

    def is_external(self):
        url = self.get_url()
        return url[0] != '#' and (url[0] != '/' or url[0:2] == '//')
