# -*- coding: utf-8 -*-
from publication_backbone.views.publication import PublicationListHybridView
from publication_backbone import conf as config

#==============================================================================
# PromotionListHybridView
#==============================================================================
class PromotionListHybridView(PublicationListHybridView):

    js_template_name_suffix = '_promotion_list'
    template_name_suffix = '_promotion_list'

    def get_context_data(self, **kwargs):
        context = super(PromotionListHybridView, self).get_context_data(**kwargs)
        category = context.get('category')
        pid = self.kwargs.get('pid') or self.request.REQUEST.get('pid') or category.id if category else 'all'

        context.update({
            'name': "%s_promotion_%s" % (context.get('name', ''), pid )
        })
        return context

    def get_paginate_by(self, queryset):
        """
        Get the number of items to paginate by, or ``None`` for no pagination.
        """
        return config.PUBLICATION_BACKBONE_PROMOTION_PER_PAGE_ITEMS_COUNT

    def get_raw_order_by(self):
        return self.kwargs.get('order_by') or self.request.REQUEST.get('order_by') or config.PUBLICATION_BACKBONE_PROMOTION_ORDER_BY