# -*- coding: utf-8 -*-
"""
This overrides the Rubric with the class loaded from the
PUBLICATION_BACKBONE_HIERARCHY_MODEL setting if it exists.
"""
from django.conf import settings

from publication_backbone.utils.loader import load_class


#==============================================================================
# Extensibility
#==============================================================================
HIERARCHY_MODEL = getattr(settings, 'PUBLICATION_BACKBONE_HIERARCHY_MODEL',
    'publication_backbone.models.defaults.rubricator.hierarchy.Hierarchy')
Hierarchy = load_class(HIERARCHY_MODEL, 'PUBLICATION_BACKBONE_HIERARCHY_MODEL')

