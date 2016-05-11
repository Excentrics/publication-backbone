#-*- coding: utf-8 -*-
from django.contrib import admin
from django.conf import settings
from django.core.management import call_command
from django.utils.translation import ugettext as _
from django.contrib.admin.util import quote

from django_mptt_admin.util import get_tree_from_queryset

from publication_backbone.admin.polymorphic_mptt_admin import PolymorphicMPTTChildModelAdmin, PolymorphicMPTTParentModelAdmin
from publication_backbone.admin.forms import CategoryAdminForm, CategoryPublicationRelationInlineForm
from publication_backbone.models import BaseCategory, Category, CategoryDivider, CategoryLink, CategoryPublicationRelation


#---------------------------------
#import logging
#logger = logging.getLogger(settings.PROJECT_NAME)
#---------------------------------


#===========================================================================================
#
#===========================================================================================
class CategoryPublicationRelation_Inline(admin.TabularInline):
    model = CategoryPublicationRelation
    extra = 1
    form = CategoryPublicationRelationInlineForm


# The common admin functionality for all derived models:
class CategoryChildAdmin(PolymorphicMPTTChildModelAdmin):
    """ Base admin class for all child models """
    base_model = BaseCategory

    save_on_top = True

    #base_form = BaseCategoryAdminForm

    class Media:
        js = [
                '/static/admin/js/list_filter_collapse.js',
              ]
        css = {
            'all': [
                '/static/admin/css/style.css',
                ]
        }

    GENERAL_FIELDSET = (None, {
        'fields': ('parent', 'name', 'slug', 'description', 'visible'),
        })

    base_fieldsets = (
        GENERAL_FIELDSET,
    )

    prepopulated_fields = {"slug": ("name",)}


# Optionally some custom admin code
class CategoryAdmin(CategoryChildAdmin):
    form = CategoryAdminForm
    inlines = [CategoryPublicationRelation_Inline,]


class DividerAdmin(CategoryChildAdmin):
    base_fieldsets = ()
    exclude = ('name', 'slug', 'description')
    prepopulated_fields = {}


class LinkAdmin(CategoryChildAdmin):
    base_fieldsets = ()
    exclude = ('description',)
    prepopulated_fields = {"slug": ("name",)}


# Create the parent admin that combines it all:
class CategoryParentAdmin(PolymorphicMPTTParentModelAdmin):
    """ The parent model admin """
    base_model = BaseCategory

    list_display = ('name', 'get_real_instance_class_name_display', 'visible', 'slug', 'path',)

    child_models = (
        (Category, CategoryAdmin), # custom admin allows custom edit/delete view.
        (CategoryDivider, DividerAdmin),
        (CategoryLink, LinkAdmin),
    )

    list_filter = ('visible',)

    search_fields = ['slug', 'name', 'path']

    def rebuild_categories(modeladmin, request, queryset):
        call_command('rebuild_categories')
    rebuild_categories.short_description = _('Rebuild categories')

    actions = ['rebuild_categories']

    tree_auto_open = 0

    autoescape = False

    class Media:
        js = [
                '/static/admin/js/list_filter_collapse.js',
              ]
        css = {
            'all': [
                '/static/admin/css/changelist.css',
                '/static/publication_backbone/lib/font-awesome/css/font-awesome.min.css',
                '/static/publication_backbone/admin/css/mptt_admin_style.css',
                '/static/publication_backbone/admin/css/category_admin_style.css',
                '/static/admin/css/style.css',
                '/static/admin/css/mptt.css',
                ]
        }

    def get_tree_data(self, qs, max_level):
        pk_attname = self.model._meta.pk.attname

        def handle_create_node(instance, node_info):
            pk = quote(getattr(instance, pk_attname))
            node_info.update(
                url=self.get_admin_url('change', (quote(pk),)),
                move_url=self.get_admin_url('move', (quote(pk),)),
                label='<span class="ex-category %(clazz)s %(visible)s">%(label)s <span class="ex-label">%(clazz_display)s</span> <i class="fa fa-eye"></i> <span class="path">%(path)s</span></span>' % {
                    'label': node_info['label'],
                    'clazz': instance._meta.object_name.lower(),
                    'clazz_display': instance._meta.verbose_name,
                    'visible': 'on' if instance.visible else 'off',
                    'path': instance.path,
                }
            )

        return get_tree_from_queryset(qs, handle_create_node, max_level)


PUBLICATION_BACKBONE_BASE_CATEGORY_MODEL = getattr(settings, 'PUBLICATION_BACKBONE_BASE_CATEGORY_MODEL', None)
if not PUBLICATION_BACKBONE_BASE_CATEGORY_MODEL:
    admin.site.register(BaseCategory, CategoryParentAdmin)

