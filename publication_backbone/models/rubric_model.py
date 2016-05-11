# -*- coding: utf-8 -*-
"""
This overrides the Rubric with the class loaded from the
PUBLICATION_BACKBONE_RUBRIC_MODEL setting if it exists.
"""
from django.conf import settings
from publication_backbone.utils.loader import load_class


#==============================================================================
# Extensibility
#==============================================================================
RUBRIC_MODEL = getattr(settings, 'PUBLICATION_BACKBONE_RUBRIC_MODEL',
    'publication_backbone.models.defaults.rubricator.rubric.Rubric')
Rubric = load_class(RUBRIC_MODEL, 'PUBLICATION_BACKBONE_RUBRIC_MODEL')

