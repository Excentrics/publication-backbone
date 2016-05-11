# -*- coding: utf-8 -*-
from django.db.models.signals import (
    m2m_changed,
    pre_delete,
    post_save
)
from django.dispatch import receiver

from publication_backbone.utils.dispatch import make_dispatch_uid
from publication_backbone.models import Publication


#==============================================================================
# Publication db event handlers
#==============================================================================
@receiver(m2m_changed, sender=Publication.rubrics.through,
          dispatch_uid=make_dispatch_uid(m2m_changed, 'normalize_rubrics_set', Publication.rubrics.through))
def normalize_rubrics_set(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Automatically normalize rubrics set
    """
    if action == 'post_add':
        if not hasattr(instance, '_during_rubrics_validation'):
            instance.validate_rubrics(pk_set)


def invalidate_prdct_after_save(sender, instance, **kwargs):
    # Clear potential rubrics ids and real rubrics ids buffers
    Publication.clear_potential_rubrics_buffer()
    Publication.clear_real_rubrics_buffer()


# connect all subclasses of base content item too
for clazz in [Publication, ] + Publication.__subclasses__():
    pre_delete.connect(invalidate_prdct_after_save, clazz,
                       dispatch_uid=make_dispatch_uid(pre_delete, invalidate_prdct_after_save, clazz))

    post_save.connect(invalidate_prdct_after_save, clazz,
                      dispatch_uid=make_dispatch_uid(post_save, invalidate_prdct_after_save, clazz))