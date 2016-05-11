# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from publication_backbone.models import BaseCategory
from publication_backbone.models_bases.category import RubricMixIn
from publication_backbone.models_bases.managers import CategoryManager


#==============================================================================
# Category
#==============================================================================
class Category(BaseCategory, RubricMixIn):

    objects = CategoryManager()

    class Meta:
        abstract = False
        app_label = 'publication_backbone'
        verbose_name = _('category')
        verbose_name_plural = _('publication categories')

