# -*- coding: utf-8 -*-
import re

from django.db import models
from django.db.models import Max, Min
from django.utils.translation import ugettext_lazy as _

from polymorphic.polymorphic_model import PolymorphicModel

from publication_backbone.models_bases.mixins import PolymorphicModelMixin, PlaceholderImageMixin
from publication_backbone.models_bases.publication import PublicationCharacteristicOrMarkSet
from publication_backbone.models import Rubric, PublicationCharacteristicOrMark
from django.utils import timezone
from datetime import datetime


#==============================================================================
# BaseGroup model
#==============================================================================
class BasePublicationGroup(PlaceholderImageMixin, PolymorphicModelMixin, PolymorphicModel):
    """
    A basic group for publications.
    """
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    slug = models.SlugField(verbose_name=_('Slug'), unique=True)
    date_added = models.DateTimeField(default=datetime.now, verbose_name=_('Date added'))
    last_modified = models.DateTimeField(auto_now=True, verbose_name=_('Last modified'))

    class Meta:
        abstract = True
        app_label = 'publication'
        verbose_name = _('Publication Group')
        verbose_name_plural = _('Publication Groups')

    def __unicode__(self):
        return self.name

    def get_name(self):
        """
        Return the name of current group (base)
        """
        return self.name

    def get_publication_reference(self):
        """
        Return publication reference of current group
        """
        return unicode("grp%s" % self.pk)

    @staticmethod
    def get_pk_by_publication_reference(value):
        """
        Return pk by publication reference of current group
        """
        m = re.match(r'^grp(?P<pk>[0-9]+)$', value)
        return m.group('pk') if m else None

    def get_image(self):
        """
        Return main image of current group if exist
        """
        if not hasattr(self, '_BasePublicationGroup__image_cache'):
            publication_image_model = self.publications.model.images.related.model
            try:
                self.__image_cache = publication_image_model.objects.filter(
                    publication__group_id__exact=self.pk, publication__active__exact=True
                ).values_list('picture', flat=True).order_by('-publication__date_added', 'sort')[0]
            except IndexError:
                self.__image_cache = None
        return self.__image_cache

    def get_date_added(self):
        """
        Return the price for current item (base)
        """
        if not hasattr(self, '_BaseProductGroup__date_added_cache'):
            date_added = self.publications.active().aggregate(min_date=Min('date_added'), max_date=Max('date_added'))
            show_date_exists = self.publications.active().filter(show_date=True).exists()
            if show_date_exists:
                if date_added['min_date'] is None:
                    date_added['min_date'] = timezone.now
                if date_added['max_date'] is None:
                    date_added['max_date'] = timezone.now
                self.__date_added_cache = [date_added['min_date'], date_added['max_date']]
            else:
                self.__date_added_cache = [None, None]

        return self.__date_added_cache

    def get_characteristics(self):
        """
        Return all characteristics objects of current publication group
        """
        if not hasattr(self, '_BasePublicationGroup__characteristics_cache'):
            tree_opts = Rubric._mptt_meta
            self.__characteristics_cache = PublicationCharacteristicOrMarkSet(self.get_active_rubrics_for_characteristics(),
                                                          self.get_additional_characteristics(),
                                                          Rubric.ATTRIBUTE_IS_CHARACTERISTIC,
                                                          tree_opts)
        return self.__characteristics_cache

    def get_marks(self):
        """
        Return all attributes objects of current publication group
        """
        if not hasattr(self, '_BasePublicationGroupt__marks_cache'):
            tree_opts = Rubric._mptt_meta
            self.__marks_cache = PublicationCharacteristicOrMarkSet(self.get_active_rubrics_for_marks(),
                                                          self.get_additional_marks(),
                                                          Rubric.ATTRIBUTE_IS_MARK,
                                                          tree_opts)
        return self.__marks_cache

    def get_active_rubrics_for_characteristics(self):
        """
        Return rubrics for characteristics of current publication group
        """
        if not hasattr(self, '_BasePublicationGroup__active_rubrics_for_characteristics_cache'):
            tree_opts = Rubric._mptt_meta
            descendants_ids = Rubric().get_all_active_characteristics_descendants_ids()
            rubrics_ids = self.publications.filter(rubrics__id__in=descendants_ids).values_list('rubrics__id', flat=True).distinct()
            self.__active_rubrics_for_characteristics_cache = list(
                Rubric.objects.filter(id__in=list(rubrics_ids)).order_by(tree_opts.tree_id_attr, tree_opts.left_attr))
        return self.__active_rubrics_for_characteristics_cache

    def get_active_rubrics_for_marks(self):
        """
        Return rubrics for marks of current publication group
        """
        if not hasattr(self, '_BasePublicationGroup__active_rubrics_for_marks_cache'):
            tree_opts = Rubric._mptt_meta
            descendants_ids = Rubric().get_all_active_marks_descendants_ids()
            rubrics_ids = self.publications.filter(rubrics__id__in=descendants_ids).values_list('rubrics__id', flat=True).distinct()
            self.__active_rubrics_for_marks_cache = list(
                Rubric.objects.filter(id__in=list(rubrics_ids)).order_by(tree_opts.tree_id_attr, tree_opts.left_attr))
        return self.__active_rubrics_for_marks_cache

    def get_additional_characteristics_or_marks_ids(self):
        """
        Return additional attributes ids of current publication group
        """
        if not hasattr(self, '_BasePublicationGroup__additional_characteristics_or_marks_ids_cache'):
            self.__additional_characteristics_or_marks_ids_cache = list(
                self.publications.values_list('additional_characteristics_or_marks__id', flat=True).distinct())
        return self.__additional_characteristics_or_marks_ids_cache

    def get_additional_characteristics(self):
        """
        Return additional characteristics of current publication group
        """
        if not hasattr(self, '_BasePublicationGroup__additional_characteristics_cache'):
            tree_opts = Rubric._mptt_meta
            self.__additional_characteristics_cache = PublicationCharacteristicOrMark.objects.filter(
                    id__in=self.get_additional_characteristics_or_marks_ids(), rubric__attribute_mode=Rubric.ATTRIBUTE_IS_CHARACTERISTIC).\
                order_by('rubric__%s' % tree_opts.tree_id_attr, 'rubric__%s' % tree_opts.left_attr)
        return self.__additional_characteristics_cache

    def get_additional_marks(self):
        """
        Return additional marks of current publication group
        """
        if not hasattr(self, '_BasePublicationGroup__additional_marks_cache'):
            tree_opts = Rubric._mptt_meta
            self.__additional_marks_cache = PublicationCharacteristicOrMark.objects.filter(
                    id__in=self.get_additional_characteristics_or_marks_ids(), rubric__attribute_mode=Rubric.ATTRIBUTE_IS_MARK).\
                order_by('rubric__%s' % tree_opts.tree_id_attr, 'rubric__%s' % tree_opts.left_attr)
        return self.__additional_marks_cache

    @models.permalink
    def get_absolute_url(self):
        """
        Return url to current publication group detail
        """
        return ('publication_group_detail', (), {'slug': self.slug})