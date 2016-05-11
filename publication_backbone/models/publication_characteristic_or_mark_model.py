# -*- coding: utf-8 -*-
"""
This overrides the PublicationCharacteristicOrMark with the class loaded from the
PUBLICATION_BACKBONE_PUBLICATION_CHARACTERISTIC_OR_MARK_MODEL setting if it exists.
"""
from django.conf import settings
from publication_backbone.utils.loader import load_class


#==============================================================================
# Extensibility
#==============================================================================
PUBLICATION_CHARACTERISTIC_OR_MARK_MODEL = getattr(settings, 'PUBLICATION_BACKBONE_PUBLICATION_CHARACTERISTIC_OR_MARK_MODEL',
    'publication_backbone.models.defaults.publication_characteristic_or_mark.PublicationCharacteristicOrMark')
PublicationCharacteristicOrMark = load_class(PUBLICATION_CHARACTERISTIC_OR_MARK_MODEL,
                                             'PUBLICATION_BACKBONE_PUBLICATION_CHARACTERISTIC_OR_MARK_MODEL')



