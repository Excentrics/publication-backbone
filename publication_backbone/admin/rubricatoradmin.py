#-*- coding: utf-8 -*-
from django.contrib import admin
from django.conf import settings
from django.core.management import call_command
from django.utils.translation import ugettext as _
from django.contrib.admin.util import quote

from changerubrictypeadmin import ChangeTypeModelAdmin

from sorl.thumbnail.admin import AdminImageMixin

from django_mptt_admin.util import get_tree_from_queryset

from bitfield import BitField
from bitfield.forms import BitFieldCheckboxSelectMultiple
from bitfield.admin import BitFieldListFilter

from publication_backbone.admin.forms import RubricAdminForm
from publication_backbone.admin.polymorphic_mptt_admin import PolymorphicMPTTChildModelAdmin, PolymorphicMPTTParentModelAdmin
from publication_backbone.admin.actions import merge_rubrics, make_rubrics_by_publications_attributes

from publication_backbone.models import (
    Rubric,
    Facet,
    Hierarchy,
    Determinant,
)


# The common admin functionality for all derived models:
class RubricChildAdmin(AdminImageMixin, PolymorphicMPTTChildModelAdmin):
    """ Base admin class for all child models """
    base_model = Rubric

    base_form = RubricAdminForm

    save_on_top = True

    class Media:
        css = {
            'all': [
                '/static/publication_backbone/admin/css/rubricator_child_admin_style.css',
                ]
        }

    GENERAL_FIELDSET = (None, {
        'fields': ('name', 'slug', 'parent', 'display_mode', 'attribute_mode', 'tags', 'active', 'description' ),
    })

    base_fieldsets = (
        GENERAL_FIELDSET,
    )

    exclude = ['image']

    prepopulated_fields = {"slug": ("name",)}

    formfield_overrides = {
        BitField: {'widget': BitFieldCheckboxSelectMultiple},
    }

if not settings.DEBUG:
    RubricChildAdmin.exclude += ['system_flags']


# Optionally some custom admin code
class FacetAdmin(RubricChildAdmin):
    form = RubricAdminForm


class HierarchyAdmin(RubricChildAdmin):
    form = RubricAdminForm


class DeterminantAdmin(RubricChildAdmin):
    form = RubricAdminForm


# Create the parent admin that combines it all:
class RubricParentAdmin(ChangeTypeModelAdmin, PolymorphicMPTTParentModelAdmin):
    """ The parent model admin """
    base_model =  Rubric

    save_on_top = True

    list_display = ('name', 'get_real_instance_class_name_display', 'active', 'path', )

    child_models = (
        (Facet, FacetAdmin), # custom admin allows custom edit/delete view.
        (Hierarchy, HierarchyAdmin),
        (Determinant, DeterminantAdmin),
    )

    list_filter = ('active', 'display_mode', 'attribute_mode', ('system_flags', BitFieldListFilter),)

    search_fields = ['path', 'name', 'tags']

    def rebuild_rubricator(modeladmin, request, queryset):
        call_command('rebuild_rubricator')
    rebuild_rubricator.short_description = _('Rebuild rubricator')

    actions = ['rebuild_rubricator', make_rubrics_by_publications_attributes]

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
                '/static/publication_backbone/admin/css/rubricator_admin_style.css',
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
                label='<span class="ex-rubric %(method)s %(active)s%(is_characteristic)s%(is_mark)s%(is_relation)s%(has_system_flags)s">%(label)s <i class="fa fa-exclamation-triangle ex-has-system-flags"></i> <i class="fa fa-list ex-characteristic"></i> <i class="fa fa-tags ex-mark"></i> <i class="fa fa-link ex-relation"></i><span class="ex-label">%(method_display)s</span> <i class="fa fa-power-off"></i> %(tags)s<span class="path">%(path)s</span></span>' % {
                    'label': node_info['label'],
                    'method': instance.get_classification_method(),
                    'method_display': instance.get_classification_method_display(),
                    'active': 'on' if instance.active else 'off',
                    'is_characteristic': ' is-characteristic' if instance.attribute_mode == Rubric.ATTRIBUTE_IS_CHARACTERISTIC else '',
                    'is_mark': ' is-mark' if instance.attribute_mode == Rubric.ATTRIBUTE_IS_MARK else '',
                    'is_relation': ' is-relation' if instance.attribute_mode == Rubric.ATTRIBUTE_IS_RELATION else '',
                    'has_system_flags': ' has-system-flags' if instance.system_flags else '',
                    'path': instance.path,
                    'tags': ''.join(['<span class="ex-label tag">%s</span>' % tag for tag in instance.tags.split()]) if instance.tags else ''
                }
            )
        return get_tree_from_queryset(qs, handle_create_node, max_level)


RUBRIC_MODEL = getattr(settings, 'PUBLICATION_BACKBONE_RUBRIC_MODEL', None)
if not RUBRIC_MODEL:
    admin.site.register(Rubric, RubricParentAdmin)

