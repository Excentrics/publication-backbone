# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from django.db.models import Q
from django.db.models.query import EmptyQuerySet

import operator

from mptt.models import MPTTModel, MPTTModelBase
from mptt.fields import TreeForeignKey

from polymorphic import PolymorphicModel
from polymorphic.base import PolymorphicModelBase

from publication_backbone.models_bases.polymorphic_mptt.managers import PolymorphicMPTTModelManager

from publication_backbone.models_bases.polymorphic_mptt.signals import (
    move_to_done,
    pre_save_polymorphic_mptt,
    post_save_polymorphic_mptt,
)


def get_base_polymorphic_model(ChildModel):
    """
    First model in the inheritance chain that inherited from the PolymorphicMPTTModel
    """
    for Model in reversed(ChildModel.mro()):
        if isinstance(Model, PolymorphicMPTTModelBase) and not Model._meta.abstract:
            return Model
    return None


class PolymorphicMPTTModelBase(MPTTModelBase, PolymorphicModelBase):
    """
    Metaclass for all polymorphic models.
    Needed to support both MPTT and Polymorphic metaclasses.
    """
    pass


class PolymorphicTreeForeignKey(TreeForeignKey):
    """
    A foreignkey that limits the node types the parent can be.
    """
    default_error_messages = {
        'no_children_allowed': _("The selected node cannot have child nodes."),
        'no_child_of_itself': _("A node may not be made a child of itself."),
        }

    def clean(self, value, model_instance):
        value = super(PolymorphicTreeForeignKey, self).clean(value, model_instance)
        self._validate_parent(value, model_instance)
        return value

    def _validate_parent(self, value, model_instance):
        if not value:
            return
        elif isinstance(value, (int, long)):
            base_model = get_base_polymorphic_model(model_instance.__class__)
            parent = base_model._default_manager.get(pk=value)
            if value == model_instance.pk:
                raise ValidationError(self.error_messages['no_child_of_itself'])
            if not parent.can_have_children:
                raise ValidationError(self.error_messages['no_children_allowed'])
        else:
            raise ValueError("Unknown parent value")

#TODO: delete south
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([
        (
            [PolymorphicTreeForeignKey],
            [],
            {},
        ),
    ], ["^publication_backbone\.models_bases\.polymorphic_mptt\.models\.PolymorphicTreeForeignKey"])
except ImportError:
    pass


class PolymorphicMPTTModel(MPTTModel, PolymorphicModel):
    """
    The base class for all nodes; a mapping of an URL to content (e.g. a HTML page, text file, blog, etc..)
    """
    __metaclass__ = PolymorphicMPTTModelBase

    #: Whether the node type allows to have children.
    can_have_children = True

    # Django fields
    objects = PolymorphicMPTTModelManager()

    class Meta:
        abstract = True

    def get_real_instance_class(self):
        if not hasattr(self, '_real_instance_class_cache'):
            if self.polymorphic_ctype_id is not None:
                self._real_instance_class_cache = super(PolymorphicMPTTModel, self).get_real_instance_class()
            else:
                self._real_instance_class_cache = self.__class__
        return self._real_instance_class_cache

    def get_real_instance(self):
        if not hasattr(self, '_real_instance_cache'):
            self._real_instance_cache = super(PolymorphicMPTTModel, self).get_real_instance()
        return self._real_instance_cache

    def get_base_instance_class(self):
        if not hasattr(self, '_base_instance_class_cache'):
            self._base_instance_class_cache = get_base_polymorphic_model(self.__class__)
        return self._base_instance_class_cache

    def get_base_instance(self):
        if not hasattr(self, '_base_instance_cache'):
            model_class = self.get_base_instance_class()
            try:
                self._base_instance_cache = model_class.objects.non_polymorphic().get(pk=self.pk)
            except model_class.DoesNotExist:
                self._base_instance_cache = self.get_base_instance_class()()
        return self._base_instance_cache

    def get_real_instance_class_name(self):
        return self.get_real_instance_class().__name__

    def get_real_instance_class_name_display(self):
        return self.get_real_instance_class()._meta.verbose_name
    get_real_instance_class_name_display.short_description = _('type')

    def move_to(self, target, position='first-child'):
        prev_parent = self.parent
        super(PolymorphicMPTTModel, self).move_to(target, position)
        move_to_done.send(sender=self.get_real_instance_class(),
                          instance=self.get_real_instance(),
                          target=target.get_real_instance(),
                          position=position,
                          prev_parent=prev_parent)

    def save(self, *args, **kwargs):
        real_instance_class = self.get_real_instance_class()
        real_instance = self.get_real_instance()
        pre_save_polymorphic_mptt.send(sender=real_instance_class, instance=real_instance)
        result = super(PolymorphicMPTTModel, self).save(*args, **kwargs)
        post_save_polymorphic_mptt.send(sender=real_instance_class, instance=real_instance)
        return result


def get_queryset_descendants(nodes, include_self=False):
    if not nodes:
        return EmptyQuerySet(PolymorphicMPTTModel) #HACK: Emulate PolymorphicMPTTModel.objects.none(), because PolymorphicMPTTModel is abstract
    filters = []
    Model = nodes[0].get_base_instance_class()
    if include_self:
        for n in nodes:
            lft, rght = n.lft - 1, n.rght + 1
            filters.append(Q(tree_id=n.tree_id, lft__gt=lft, rght__lt=rght))
    else:
        for n in nodes:
            if n.get_descendant_count():
                lft, rght = n.lft, n.rght
                filters.append(Q(tree_id=n.tree_id, lft__gt=lft, rght__lt=rght))
    if filters:
        return Model.objects.filter(reduce(operator.or_, filters))
    else:
        return Model.objects.filter(id__isnull=True)
