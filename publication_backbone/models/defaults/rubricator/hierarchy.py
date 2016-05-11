# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from publication_backbone.models_bases.rubricator import (
    HierarchyMixIn,
    FacetFilteringMixin,
    )

from publication_backbone.models import Rubric


class Hierarchy(FacetFilteringMixin, HierarchyMixIn, Rubric):

    #custom = models.CharField(verbose_name=_('custom'), max_length=255)

    class Meta:
        abstract = False
        app_label = 'publication_backbone'
        verbose_name = _('hierarchy')
        verbose_name_plural = _('hierarchy rubricator')

