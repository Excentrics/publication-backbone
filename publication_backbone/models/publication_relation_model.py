# -*- coding: utf-8 -*-
"""
This overrides the PublicationRelation with the class loaded from the
PUBLICATION_BACKBONE_PUBLICATION_RELATION_MODEL setting if it exists.
"""
from django.conf import settings
from publication_backbone.utils.loader import load_class

#==============================================================================
# Extensibility
#==============================================================================
PUBLICATION_RELATION_MODEL = getattr(settings, 'PUBLICATION_BACKBONE_PUBLICATION_RELATION_MODEL',
    'publication_backbone.models.defaults.publication_relation.PublicationRelation')
PublicationRelation = load_class(PUBLICATION_RELATION_MODEL, 'PUBLICATION_BACKBONE_PUBLICATION_RELATION_MODEL')
