# -*- coding: utf-8 -*-
"""
This overrides the Category with the class loaded from the
PUBLICATION_BACKBONE_BASE_CATEGORY_MODEL setting if it exists.
"""
from django.conf import settings
from publication_backbone.utils.loader import load_class


#==============================================================================
# Extensibility
#==============================================================================
BASE_CATEGORY_MODEL = getattr(settings, 'PUBLICATION_BACKBONE_BASE_CATEGORY_MODEL',
    'publication_backbone.models.defaults.category.base_category.BaseCategory')
BaseCategory = load_class(BASE_CATEGORY_MODEL, 'PUBLICATION_BACKBONE_BASE_CATEGORY_MODEL')
