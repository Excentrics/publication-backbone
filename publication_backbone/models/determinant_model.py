# -*- coding: utf-8 -*-
"""
This overrides the Rubric with the class loaded from the
PUBLICATION_BACKBONE_DETERMINANT_MODEL setting if it exists.
"""
from django.conf import settings

from publication_backbone.utils.loader import load_class


#==============================================================================
# Extensibility
#==============================================================================
DETERMINANT_MODEL = getattr(settings, 'PUBLICATION_BACKBONE_DETERMINANT_MODEL',
    'publication_backbone.models.defaults.rubricator.determinant.Determinant')
Determinant = load_class(DETERMINANT_MODEL, 'PUBLICATION_BACKBONE_DETERMINANT_MODEL')


