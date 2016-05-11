# -*- coding: utf-8 -*-
#from django.conf import settings

from django.core.cache import cache
from django.db.models.signals import (
    pre_delete,
    #post_save
)
from django.db.utils import DatabaseError

from publication_backbone.utils.dispatch import make_dispatch_uid
from publication_backbone.models import Rubric, Hierarchy, Facet, Publication

from publication_backbone.models_bases.rubricator import RubricInfo

from publication_backbone.models_bases.polymorphic_mptt.signals import (
    move_to_done,
    pre_save_polymorphic_mptt,
    post_save_polymorphic_mptt,
)

#==============================================================================
# Rubric db event handlers
#==============================================================================
def invalidate_rbrc_before_save(sender, instance, **kwargs):
    # active children cache
    if not instance.id is None:
        try:
            original = sender._default_manager.get(pk=instance.id)
            if original.parent_id != instance.parent_id and not original.parent_id is None:
                key = sender.RUBRIC_ACTIVE_CHILDREN_CACHE_KEY_PATTERN % {'id': original.parent_id}
                cache.delete(key)
        except sender.DoesNotExist:
            pass


def invalidate_rbrc_after_save(sender, instance, **kwargs):
    # active children cache, characteristic and mark descendants cache, category active rubric cache count
    if not instance.id is None:
        Category = sender.category_set.related.model
        keys = [sender.RUBRIC_ACTIVE_CHILDREN_CACHE_KEY_PATTERN % {'id': instance.id},
                sender.RUBRIC_CHARACTERISTIC_DESCENDANTS_IDS_CACHE_KEY,
                sender.RUBRIC_MARK_DESCENDANTS_IDS_CACHE_KEY,
                Category.CATEGORY_ACTIVE_RUBRIC_COUNT_CACHE_KEY,
                Category.CATEGORY_ACTIVE_RUBRIC_IDS_CACHE_KEY]
        if not instance.parent_id is None:
            keys.append(sender.RUBRIC_ACTIVE_CHILDREN_CACHE_KEY_PATTERN % {'id': instance.parent_id})
        keys.extend([sender.RUBRIC_ATTRIBUTES_ANCESTORS_CACHE_KEY_PATTERN % {'id': id, 'attribute_mode': attribute_mode}
            for id in instance.get_descendants(include_self=True).values_list('id', flat=True)
            for attribute_mode in (Rubric.ATTRIBUTE_IS_CHARACTERISTIC, Rubric.ATTRIBUTE_IS_MARK,)])
        cache.delete_many(keys)

        # Clear decompress buffer
        RubricInfo.clear_decompress_buffer()

        # Clear potential rubrics ids and real rubrics ids buffers
        Publication.clear_potential_rubrics_buffer()
        Publication.clear_real_rubrics_buffer()



def invalidate_rbrc_after_move(sender, instance, target, position, prev_parent, **kwargs):
    # active children cache
    if not prev_parent is None:
        keys = [sender.RUBRIC_ACTIVE_CHILDREN_CACHE_KEY_PATTERN % {'id': prev_parent.id},
                sender.RUBRIC_CHARACTERISTIC_DESCENDANTS_IDS_CACHE_KEY,
                sender.RUBRIC_MARK_DESCENDANTS_IDS_CACHE_KEY]
        cache.delete_many(keys)
    invalidate_rbrc_after_save(sender, instance, **kwargs)


# connect all subclasses of base content item too
for clazz in Rubric.__subclasses__():
    pre_save_polymorphic_mptt.connect(invalidate_rbrc_before_save, clazz,
                                      dispatch_uid=make_dispatch_uid(pre_save_polymorphic_mptt,
                                                                     invalidate_rbrc_before_save,
                                                                     clazz))
    post_save_polymorphic_mptt.connect(invalidate_rbrc_after_save, clazz,
                                       dispatch_uid=make_dispatch_uid(post_save_polymorphic_mptt,
                                                                      invalidate_rbrc_after_save,
                                                                      clazz))
    pre_delete.connect(invalidate_rbrc_after_save, clazz,
                       dispatch_uid=make_dispatch_uid(pre_delete, invalidate_rbrc_after_save, clazz))
    move_to_done.connect(invalidate_rbrc_after_move, clazz,
                         dispatch_uid=make_dispatch_uid(move_to_done,
                                                        invalidate_rbrc_after_move,
                                                        clazz))


#==============================================================================
# Validate rubricator tree system structure
#==============================================================================
try:

    system_flags = Rubric.system_flags.delete_restriction | \
        Rubric.system_flags.change_parent_restriction | \
        Rubric.system_flags.change_slug_restriction | \
        Rubric.system_flags.change_subclass_restriction | \
        Rubric.system_flags.has_child_restriction | \
        Rubric.system_flags.tagged_restriction


#==============================================================================
# added_year section
#==============================================================================
    # added year
    try:
        added_year = Hierarchy.objects.get(slug=Publication.ADDED_YEAR[0])
    except Hierarchy.DoesNotExist:
        added_year = Hierarchy(
            slug=Publication.ADDED_YEAR[0],
            name=Publication.ADDED_YEAR[1],
            parent=None,
            system_flags=system_flags)
        added_year.save()


#==============================================================================
# added_month section
#==============================================================================
    # added month
    try:
        added_month = Facet.objects.get(slug=Publication.ADDED_MONTH[0])
    except Facet.DoesNotExist:
        added_month = Facet(
            slug=Publication.ADDED_MONTH[0],
            name=Publication.ADDED_MONTH[1],
            parent=None,
            system_flags=system_flags)
        added_month.save()

    for i in range(1, 13):
        month_key = Publication.ADDED_MONTH_KEY % i
        try:
            month = Facet.objects.get(slug=month_key)
        except Facet.DoesNotExist:
            month = Facet(slug=month_key,
                          name="%02d" % i,
                          parent=added_month,
                          system_flags=system_flags)
            month.save()


#==============================================================================
# added_day section
#==============================================================================
    # added day
    try:
        added_day = Facet.objects.get(slug=Publication.ADDED_DAY[0])
    except Facet.DoesNotExist:
        added_day = Facet(
            slug=Publication.ADDED_DAY[0],
            name=Publication.ADDED_DAY[1],
            parent=None,
            system_flags=system_flags)
        added_day.save()
    day_ranges = ((1, 11), (11, 21), (21, 32))
    for r in day_ranges:
        # added day range
        day_range_key = Publication.ADDED_DAY_RANGE_KEY % (r[0], r[1] - 1)
        try:
            added_day_range = Facet.objects.get(slug=day_range_key)
        except Facet.DoesNotExist:
            added_day_range = Facet(
                slug=day_range_key,
                name="%s - %s" % (r[0], r[1] - 1),
                parent=added_day,
                system_flags=system_flags)
            added_day_range.save()
        for i in range(r[0], r[1]):
            day_key = Publication.ADDED_DAY_KEY % i
            try:
                day = Facet.objects.get(slug=day_key)
            except Facet.DoesNotExist:
                day = Facet(slug=day_key,
                            name="%02d" % i,
                            parent=added_day_range,
                            system_flags=system_flags)
                day.save()


#==============================================================================
# Stock status section
#==============================================================================

    """
    is_validate_stock_status = getattr(settings, 'PUBLICATION_BACKBONE_VALIDATE_RUBRIC_STOCK_STATUS', True)
    if is_validate_stock_status:
        # stock status
        try:
            stock_status = Hierarchy.objects.get(slug=Publication.STOCK_STATUS[0])
        except Hierarchy.DoesNotExist:
            stock_status = Hierarchy(
                slug=Publication.STOCK_STATUS[0],
                name=Publication.STOCK_STATUS[1],
                parent=None,
                system_flags=system_flags)
            stock_status.save()


        # out of stock
        try:
            out_of_stock = Facet.objects.get(slug=Publication.OUT_OF_STOCK[0])
        except Facet.DoesNotExist:
            out_of_stock = Facet(slug=Publication.OUT_OF_STOCK[0],
                                 name=Publication.OUT_OF_STOCK[1],
                                 parent=stock_status,
                                 system_flags=system_flags)
            out_of_stock.save()


        # in stock
        try:
            in_stock = Facet.objects.get(slug=Publication.IN_STOCK[0])
        except Facet.DoesNotExist:
            in_stock = Facet(slug=Publication.IN_STOCK[0],
                             name=Publication.IN_STOCK[1],
                             parent=stock_status,
                             system_flags=system_flags)
            in_stock.save()


        # sold out
        try:
            sold_out = Facet.objects.get(slug=Publication.SOLD_OUT[0])
        except Facet.DoesNotExist:
            sold_out = Facet(slug=Publication.SOLD_OUT[0],
                             name=Publication.SOLD_OUT[1],
                             parent=stock_status,
                             system_flags=system_flags)
            sold_out.save()
    """


#==============================================================================
# Estimated delivery status section
#==============================================================================

    """
    is_validate_delivery_status = getattr(settings, 'PUBLICATION_BACKBONE_VALIDATE_RUBRIC_DELIVERY_STATUS', True)
    if is_validate_delivery_status:
        # estimated delivery status
        try:
            estimated_delivery_status = Hierarchy.objects.get(slug=Publication.ESTIMATED_DELIVERY_STATUS[0])
        except Hierarchy.DoesNotExist:
            estimated_delivery_status = Hierarchy(
                slug=Publication.ESTIMATED_DELIVERY_STATUS[0],
                name=Publication.ESTIMATED_DELIVERY_STATUS[1],
                parent=None,
                system_flags=system_flags)
            estimated_delivery_status.save()

        # estimated delivery defined
        try:
            estimated_delivery_defined = Facet.objects.get(slug=Publication.ESTIMATED_DELIVERY_DEFINED[0])
        except Facet.DoesNotExist:
            estimated_delivery_defined = Facet(slug=Publication.ESTIMATED_DELIVERY_DEFINED[0],
                                 name=Publication.ESTIMATED_DELIVERY_DEFINED[1],
                                 parent=estimated_delivery_status,
                                 system_flags=system_flags)
            estimated_delivery_defined.save()

        # estimated delivery not defined
        try:
            estimated_delivery_not_defined = Facet.objects.get(slug=Publication.ESTIMATED_DELIVERY_NOT_DEFINED[0])
        except Facet.DoesNotExist:
            estimated_delivery_not_defined = Facet(slug=Publication.ESTIMATED_DELIVERY_NOT_DEFINED[0],
                                 name=Publication.ESTIMATED_DELIVERY_NOT_DEFINED[1],
                                 parent=estimated_delivery_status,
                                 system_flags=system_flags)
            estimated_delivery_not_defined.save()
    """

#==============================================================================
# Price status section
#==============================================================================
    """
    is_validate_price_status = getattr(settings, 'PUBLICATION_BACKBONE_VALIDATE_RUBRIC_PRICE_STATUS', True)
    if is_validate_price_status:
        # price status
        try:
            price_status = Hierarchy.objects.get(slug=Publication.PRICE_STATUS[0])
        except Hierarchy.DoesNotExist:
            price_status = Hierarchy(
                slug=Publication.PRICE_STATUS[0],
                name=Publication.PRICE_STATUS[1],
                parent=None,
                system_flags=system_flags)
            price_status.save()

        # price defined
        try:
            price_defined = Facet.objects.get(slug=Publication.PRICE_DEFINED[0])
        except Facet.DoesNotExist:
            price_defined = Facet(slug=Publication.PRICE_DEFINED[0],
                                 name=Publication.PRICE_DEFINED[1],
                                 parent=price_status,
                                 system_flags=system_flags)
            price_defined.save()

        # price not defined
        try:
            price_not_defined = Facet.objects.get(slug=Publication.PRICE_NOT_DEFINED[0])
        except Facet.DoesNotExist:
            price_not_defined = Facet(slug=Publication.PRICE_NOT_DEFINED[0],
                                 name=Publication.PRICE_NOT_DEFINED[1],
                                 parent=price_status,
                                 system_flags=system_flags)
            price_not_defined.save()
    """


except DatabaseError as e:
    # south migration HACK
    print e.args


