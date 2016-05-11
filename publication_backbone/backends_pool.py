#-*- coding: utf-8 -*-
from django.conf import settings
from publication_backbone.search.api import SearchAPI
from publication_backbone.utils.loader import load_class


class BackendsPool(object):
    """
    A pool for backends.
    It handles loading backend modules (both shipping and payment backends),
    and keeping a cached copy of the classes in-memory (so that the backends
    aren't loaded from file every time one requests them)
    """

    SEARCH = 'PUBLICATION_BACKBONE_SEARCH_BACKENDS'
    SEARCH_PUBLICATION_INTERFACE = SearchAPI()

    def __init__(self, use_cache=True):
        """
        The use_cache parameter is mostly used for testing, since setting it
        to false will trigger reloading from disk
        """
        self._search_backends_list = []
        self.use_cache = use_cache


    def get_search_backends_list(self):
        """
        Returns the list of payment backends, as instances, from the list of
        backends defined in settings.PUBLICATION_BACKBONE_SEARCH_BACKENDS
        """
        if self._search_backends_list and self.use_cache:
            return self._search_backends_list
        else:
            self._search_backends_list = self._load_backends_list(
                self.SEARCH, self.SEARCH_PUBLICATION_INTERFACE)
            return self._search_backends_list

    def _check_backend_for_validity(self, backend_instance):
        """
        This enforces having a valid name and url namespace defined.
        Backends, both shipping and payment are namespaced in respectively
        /pay/ and /ship/ URL spaces, so as to avoid name clashes.

        "Namespaces are one honking great idea -- let's do more of those!"
        """
        backend_name = getattr(backend_instance, 'backend_name', "")
        if not backend_name:
            d_tuple = (str(backend_instance), str(type(backend_instance)))
            raise NotImplementedError(
                'One of your backends ("%s" of type "%s") lacks a name, please'
                ' define one.' % d_tuple)

        url_namespace = getattr(backend_instance, 'url_namespace', "")
        if not url_namespace:
            raise NotImplementedError(
                'Please set a namespace for backend "%s"' %
                    backend_instance.backend_name)

    def _load_backends_list(self, setting_name, publication_object):
        """ This actually loads the backends from disk"""
        result = []
        if not getattr(settings, setting_name, None):
            return result

        for backend_path in getattr(settings, setting_name, None):
            # The load_class function takes care of the classloading. It
            # returns a CLASS, not an INSTANCE!
            mod_class = load_class(backend_path, setting_name)

            # Seems like it is a real, valid class - let's instanciate it!
            # This is where the backends receive their self.publication reference!
            mod_instance = mod_class(publication_backbone=publication_object)

            self._check_backend_for_validity(mod_instance)

            # The backend seems valid (nothing raised), let's add it to the
            # return list.
            result.append(mod_instance)

        return result


backends_pool = BackendsPool()
