# -*- coding: utf-8 -*-
"""
This overrides the Publication with the class loaded from the
PUBLICATION_BACKBONE_PUBLICATION_MODEL setting if it exists.
"""
from django.conf import settings
from publication_backbone.utils.loader import load_class


#==============================================================================
# Extensibility
#==============================================================================
PUBLICATION_MODEL = getattr(settings, 'PUBLICATION_BACKBONE_PUBLICATION_MODEL', 'publication_backbone.models.defaults.publication.Publication')
Publication = load_class(PUBLICATION_MODEL, 'PUBLICATION_BACKBONE_PUBLICATION_MODEL')

