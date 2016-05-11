# -*- coding: utf-8 -*-
"""
This overrides the Category with the class loaded from the
PUBLICATION_BACKBONE_CATEGORY_MODEL setting if it exists.
"""
from django.conf import settings
from publication_backbone.utils.loader import load_class


#==============================================================================
# Extensibility
#==============================================================================
CATEGORY_MODEL = getattr(settings, 'PUBLICATION_BACKBONE_CATEGORY_MODEL',
    'publication_backbone.models.defaults.category.category.Category')
Category = load_class(CATEGORY_MODEL, 'PUBLICATION_BACKBONE_CATEGORY_MODEL')
