# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from constance.settings import *
from publication_backbone.models import BaseCategory


CONFIG = getattr(settings, 'PUBLICATION_BACKBONE_CONFIG', {
    'PUBLICATION_BACKBONE_CATALOG_PER_PAGE_ITEMS_COUNT': (12, _("Count of items in catalog")),
    'PUBLICATION_BACKBONE_CATALOG_ORDER_BY': ("date_added_desc", _("Item ordering: date_added_desc, name_asc, price_asc, price_desc")),
    'PUBLICATION_BACKBONE_PROMOTION_PER_PAGE_ITEMS_COUNT': (3, _("Count of items in promotion")),
    'PUBLICATION_BACKBONE_PROMOTION_ORDER_BY': ("date_added_desc", _("Item ordering in promotion: date_added_desc, name_asc, price_asc, price_desc")),
    'PUBLICATION_BACKBONE_CATALOG_THUMBNAIL_WIDTH': (300, _("Publication thumbnail image width, for example: 200")),
    'PUBLICATION_BACKBONE_CATALOG_THUMBNAIL_HEIGHT': (300, _("Publication thumbnail image height, for example: 200")),
    'PUBLICATION_BACKBONE_CATALOG_THUMBNAIL_BACKGROUND': ("#ffffff", _("Publication thumbnail image background, for example: #ffffff")),
    'PUBLICATION_BACKBONE_DEFAULT_CATALOG_TITLE': ("Catalog", _("Default catalog title")),
    'PUBLICATION_BACKBONE_CATEGORY_MENU_ORIENTATION': ("horizontal", _("Category menu orientation: horizontal, vertical")),
    'PUBLICATION_BACKBONE_CATEGORY_KEY': (BaseCategory._meta.object_name.lower(), _("Keyword for linking category widget elements")),
    'PUBLICATION_BACKBONE_LIVE_SEARCH_RESULTS': (10, _("Number of results displayed in Live search")),
    'PUBLICATION_RSS_FEED_COUNT': (10, _('Count of items in RSS feed')),
})
