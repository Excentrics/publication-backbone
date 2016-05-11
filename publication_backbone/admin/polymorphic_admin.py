#-*- coding: utf-8 -*-
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin


class PolymorphicChildModelAdmin(PolymorphicChildModelAdmin):
    """ Base admin class for all child models """
    pass


class PolymorphicParentModelAdmin(PolymorphicParentModelAdmin):
    """ The parent model admin """

    pass
