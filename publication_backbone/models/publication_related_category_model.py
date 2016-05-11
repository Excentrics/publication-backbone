# -*- coding: utf-8 -*-
"""
This overrides the PublicationRelatedCategory with the class loaded from the
PUBLICATION_BACKBONE_PUBLICATION_RELATED_CATEGORY_MODEL setting if it exists.
"""
from django.conf import settings
from publication_backbone.utils.loader import load_class


#==============================================================================
# Extensibility
#==============================================================================
PUBLICATION_RELATED_CATEGORY_MODEL = getattr(settings, 'PUBLICATION_BACKBONE_PUBLICATION_RELATED_CATEGORY_MODEL',
    'publication_backbone.models.defaults.publication_related_category.PublicationRelatedCategory')
PublicationRelatedCategory = load_class(PUBLICATION_RELATED_CATEGORY_MODEL, 'PUBLICATION_BACKBONE_PUBLICATION_RELATED_CATEGORY_MODEL')
