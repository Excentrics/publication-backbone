# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.db.models.signals import pre_delete, m2m_changed, pre_save
from django.dispatch import receiver

from publication_backbone.models_bases.polymorphic_mptt.signals import (
    move_to_done,
    pre_save_polymorphic_mptt,
    post_save_polymorphic_mptt,
)

from publication_backbone.utils.dispatch import make_dispatch_uid
from publication_backbone.models import BaseCategory, Category, CategoryLink
from publication_backbone.utils.contrib import get_unique_slug



def validate_category_path(sender, instance, raw, using, update_fields, **kwargs):
    """
    Check for duplicate category path before save category
    """
    if (not raw) and (sender._default_manager.exclude(pk=instance.pk).filter(path=instance.path).exists()) :
        ancestors = instance.get_ancestors_list()
        instance.slug = get_unique_slug(instance.slug, instance.id)
        instance.make_path(ancestors + [instance,])

# Connect validate_category_path to all categories class
for clazz in BaseCategory.__subclasses__():
    pre_save.connect(validate_category_path, clazz, dispatch_uid=make_dispatch_uid(pre_save, validate_category_path, clazz))


#==============================================================================
# Category db event handlers
#==============================================================================
@receiver(m2m_changed, sender=Category.rubrics.through,
          dispatch_uid=make_dispatch_uid(m2m_changed, 'invalidate_after_rubrics_set_changed', Category.rubrics.through))
def invalidate_after_rubrics_set_changed(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Automatically normalize rubrics set
    """
    if action == 'post_add':
        if not hasattr(instance, '_during_rubrics_validation'):
            # normalize rubrics set
            instance.validate_rubrics(pk_set)
            # clear cache
            keys = [instance.CATEGORY_ACTIVE_RUBRIC_COUNT_CACHE_KEY,
                    instance.CATEGORY_ACTIVE_RUBRIC_IDS_CACHE_KEY]
            cache.delete_many(keys)


def invalidate_ctgr_vsbl_chldrn_cache_before_save(sender, instance, **kwargs):
    if not instance.id is None:
        try:
            original = sender._default_manager.get(pk=instance.id)
            if original.parent_id != instance.parent_id and not original.parent_id is None:
                key = sender.CATEGORY_VISIBLE_CHILDREN_CACHE_KEY_PATTERN % {'id': original.parent_id}
                cache.delete(key)
        except sender.DoesNotExist:
            pass


def invalidate_ctgr_vsbl_chldrn_cache_after_save(sender, instance, **kwargs):
    if not instance.id is None:
        keys = [sender.CATEGORY_VISIBLE_CHILDREN_CACHE_KEY_PATTERN % {'id': instance.id}, ]
        if not instance.parent_id is None:
            keys.append(sender.CATEGORY_VISIBLE_CHILDREN_CACHE_KEY_PATTERN % {'id': instance.parent_id})
        cache.delete_many(keys)


def invalidate_ctgr_vsbl_chldrn_cache_after_move(sender, instance, target, position, prev_parent, **kwargs):
    if not prev_parent is None:
        key = sender.CATEGORY_VISIBLE_CHILDREN_CACHE_KEY_PATTERN % {'id': prev_parent.id}
        cache.delete(key)
    invalidate_ctgr_vsbl_chldrn_cache_after_save(sender, instance, **kwargs)


# connect all subclasses of base content item too
for clazz in BaseCategory.__subclasses__():
    pre_save_polymorphic_mptt.connect(invalidate_ctgr_vsbl_chldrn_cache_before_save, clazz,
                                      dispatch_uid=make_dispatch_uid(pre_save_polymorphic_mptt,
                                                                     invalidate_ctgr_vsbl_chldrn_cache_before_save,
                                                                     clazz))
    post_save_polymorphic_mptt.connect(invalidate_ctgr_vsbl_chldrn_cache_after_save, clazz,
                                       dispatch_uid=make_dispatch_uid(post_save_polymorphic_mptt,
                                                                      invalidate_ctgr_vsbl_chldrn_cache_after_save,
                                                                      clazz))
    pre_delete.connect(invalidate_ctgr_vsbl_chldrn_cache_after_save, clazz,
                       dispatch_uid=make_dispatch_uid(pre_delete,
                                                      invalidate_ctgr_vsbl_chldrn_cache_after_save,
                                                      clazz))
    move_to_done.connect(invalidate_ctgr_vsbl_chldrn_cache_after_move, clazz,
                         dispatch_uid=make_dispatch_uid(move_to_done,
                                                        invalidate_ctgr_vsbl_chldrn_cache_after_move,
                                                        clazz))