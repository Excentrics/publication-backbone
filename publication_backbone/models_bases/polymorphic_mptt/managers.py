# -*- coding: utf-8 -*-
from mptt.managers import TreeManager
from polymorphic import PolymorphicManager
from polymorphic.query import PolymorphicQuerySet


class PolymorphicMPTTQuerySet(PolymorphicQuerySet):
    """
    Base class for querysets
    """
    def toplevel(self):
        """
        Return all nodes which have no parent.
        """
        return self.filter(parent__isnull=True)


class PolymorphicMPTTModelManager(TreeManager, PolymorphicManager):
    """
    Base class for a model manager.
    """
    '''
    def __init__(self, queryset_class=None, *args, **kwargs):
        if not queryset_class:
            if not hasattr(self, 'queryset_class'):
                self.queryset_class = PolymorphicMPTTQuerySet
        else:
            self.queryset_class = queryset_class
        PolymorphicManager.__init__(self, self.queryset_class, *args, **kwargs)
    '''

    def toplevel(self):
        """
        Return all nodes which have no parent.
        """
        return self.get_query_set().toplevel()
