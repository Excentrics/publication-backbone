# -*- coding: utf-8 -*-
"""
This overrides the Publication with the class loaded from the
PUBLICATION_BACKBONE_PUBLICATION_IMAGE_MODEL setting if it exists.
"""
from django.conf import settings
from publication_backbone.utils.loader import load_class


#==============================================================================
# Extensibility
#==============================================================================
PUBLICATION_IMAGE_MODEL = getattr(settings, 'PUBLICATION_BACKBONE_PUBLICATION_IMAGE_MODEL',
    'publication_backbone.models.defaults.publication_image.PublicationImage')
PublicationImage = load_class(PUBLICATION_IMAGE_MODEL, 'PUBLICATION_BACKBONE_PUBLICATION_IMAGE_MODEL')

