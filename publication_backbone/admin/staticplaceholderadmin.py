# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from publication_backbone.models import StaticPlaceholder

from fluent_contents.admin import PlaceholderFieldAdmin


#===========================================================================================
# StaticPlaceholderAdmin
#===========================================================================================
class StaticPlaceholderAdmin(PlaceholderFieldAdmin):

    save_on_top = True

    actions = None

    list_display = ('name', 'slug', 'site',)

    list_display_links = ('slug', 'name')

    search_fields = ['slug', 'name', ]

    def has_delete_permission(self, request, obj=None):
            return getattr(settings, 'DEBUG', False)

    def has_add_permission(self, request):
            return getattr(settings, 'DEBUG', False)

    fieldsets = (
        (None, {
                'fields':
                    ('name', 'slug', 'site')
               }),
        (_("Contents"), {
            'fields': ('placeholder',),
            'classes': ('plugin-holder',),
        }),
    )



if not StaticPlaceholderAdmin in admin.site._registry:
    admin.site.register(StaticPlaceholder, StaticPlaceholderAdmin)

