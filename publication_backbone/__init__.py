# -*- coding: utf-8 -*-
#
default_app_config = 'publication_backbone.apps.PublicationBackboneConfig'
from django.utils.functional import LazyObject

class LazyConfig(LazyObject):

    def _setup(self):
        from publication_backbone.config import Config
        self._wrapped = Config()


conf = LazyConfig()