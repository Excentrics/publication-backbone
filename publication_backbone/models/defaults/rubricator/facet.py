# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from publication_backbone.models_bases.rubricator import (
    FacetMixIn,
    FacetFilteringMixin,
    )

from publication_backbone.models import Rubric


class Facet(FacetFilteringMixin, FacetMixIn, Rubric):

    class Meta:
        abstract = False
        app_label = 'publication_backbone'
        verbose_name = _('facet')
        verbose_name_plural = _('facet rubricator')

