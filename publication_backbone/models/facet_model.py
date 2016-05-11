# -*- coding: utf-8 -*-
"""
This overrides the Rubric with the class loaded from the
PUBLICATION_BACKBONE_FACET_MODEL setting if it exists.
"""
from django.conf import settings

from publication_backbone.utils.loader import load_class


#==============================================================================
# Extensibility
#==============================================================================
FACET_MODEL = getattr(settings, 'PUBLICATION_BACKBONE_FACET_MODEL',
    'publication_backbone.models.defaults.rubricator.facet.Facet')
Facet = load_class(FACET_MODEL, 'PUBLICATION_BACKBONE_FACET_MODEL')
