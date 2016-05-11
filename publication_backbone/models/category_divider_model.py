# -*- coding: utf-8 -*-
"""
This overrides the Category with the class loaded from the
PUBLICATION_BACKBONE_CATEGORY_DIVIDER_MODEL setting if it exists.
"""
from django.conf import settings
from publication_backbone.utils.loader import load_class


#==============================================================================
# Extensibility
#==============================================================================
CATEGORY_DIVIDER_MODEL = getattr(settings, 'PUBLICATION_BACKBONE_CATEGORY_DIVIDER_MODEL',
    'publication_backbone.models.defaults.category.category_divider.CategoryDivider')
CategoryDivider = load_class(CATEGORY_DIVIDER_MODEL, 'PUBLICATION_BACKBONE_CATEGORY_DIVIDER_MODEL')
