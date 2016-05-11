# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from publication_backbone.models_bases.rubricator import (
    DeterminantMixIn,
    #DeterminantFilteringMixin,
    )

from publication_backbone.models import Rubric


class Determinant(DeterminantMixIn, Rubric):

    class Meta:
        abstract = False
        app_label = 'publication_backbone'
        verbose_name = _('determinant')
        verbose_name_plural = _('determinant rubricator')


