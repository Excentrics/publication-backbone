# -*- coding: utf-8 -*-
"""
This overrides the PublicationGroup with the class loaded from the
PUBLICATION_BACKBONE_PUBLICATION_GROUP_MODEL setting if it exists.
"""
from django.conf import settings
from publication_backbone.utils.loader import load_class


#==============================================================================
# Extensibility
#==============================================================================
PUBLICATION_GROUP_MODEL = getattr(settings, 'PUBLICATION_BACKBONE_PUBLICATION_GROUP_MODEL',
                              'publication_backbone.models.defaults.publication_group.PublicationGroup')
PublicationGroup = load_class(PUBLICATION_GROUP_MODEL, 'PUBLICATION_BACKBONE_PUBLICATION_GROUP_MODEL')
