# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin import ListFilter
from django.utils.translation import ugettext_lazy as _

from publication_backbone.models import (
    Rubric,
    Publication,
    PublicationCharacteristicOrMark,
    PublicationRelation,
    PublicationRelatedCategory,
    PublicationImage,
)

from publication_backbone.models_bases.rubricator import RubricInfo

from publication_backbone.admin.forms import (
    PublicationAdminForm,
    PublicationCharacteristicOrMarkInlineForm,
    PublicationRelationInlineForm,
)

from sorl.thumbnail.admin import AdminImageMixin


from modelcloneadmin import ClonableModelAdmin
from actions import (
    set_selected_rubrics,
    set_description,
    set_publicationgroup,
    set_estimated_delivery,
    set_rubrics_by_attributes)

from salmonella.admin import SalmonellaMixin
from django.core.exceptions import ImproperlyConfigured
from fluent_contents.admin import PlaceholderFieldAdmin

#===========================================================================================
#
#===========================================================================================

class RubricsTreeFilter(ListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Rubrics')
    template = 'admin/filters/rubric_tree.html'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'publication_rubrics_set'

    def __init__(self, request, params, model, model_admin):
        super(RubricsTreeFilter, self).__init__(
            request, params, model, model_admin)

        if self.parameter_name is None:
            raise ImproperlyConfigured(
                "The list filter '%s' does not specify "
                "a 'parameter_name'." % self.__class__.__name__)

        if self.parameter_name in params:
            value = params.pop(self.parameter_name)
            if value:
                self.used_parameters[self.parameter_name] = value

    def has_output(self):
        return True

    def value(self):
        return self.used_parameters.get(self.parameter_name, None)

    def get_active_rubrics(self):
        return list(Rubric.objects.active())

    def get_expanded_rubrics(self):
        value = self.value()
        if value:
            values = value.split(',')
            self.expanded_rubrics = list(set(RubricInfo.decompress(Rubric, values, fix_it=False).keys()).difference(values))
        else:
            self.expanded_rubrics = list()
        return self.expanded_rubrics

    def expected_parameters(self):
        return [self.parameter_name]

    def choices(self, cl):
        value = self.value()
        if value:
            values = value.split(',')
        else:
            values = list()
        yield {
            'queryset': self.get_active_rubrics(),
            'name': self.title,
            'value': values,
            'expanded_rubrics': self.get_expanded_rubrics(),
            'is_characteristic': Rubric.ATTRIBUTE_IS_CHARACTERISTIC,
            'is_mark':Rubric.ATTRIBUTE_IS_MARK,
            'is_relation': Rubric.ATTRIBUTE_IS_RELATION
        }

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            values = self.value().split(',')
            publication_rubrics_set = list(set(RubricInfo.decompress(Rubric, values, fix_it=False).keys()))
            return queryset.make_filtering(set=publication_rubrics_set)
        else:
            return queryset


#===========================================================================================
#
#===========================================================================================
class PublicationRelatedCategory_Inline(admin.TabularInline):
    model = PublicationRelatedCategory
    extra = 1


#===========================================================================================
#
#===========================================================================================
class PublicationImage_Inline(AdminImageMixin, admin.StackedInline):
    model = PublicationImage
    extra = 1


#===========================================================================================
#
#===========================================================================================
class PublicationCharacteristicOrMark_Inline(admin.TabularInline):
    model = PublicationCharacteristicOrMark
    extra = 1
    form = PublicationCharacteristicOrMarkInlineForm


#===========================================================================================
#
#===========================================================================================
class PublicationRelation_Inline(SalmonellaMixin, admin.TabularInline):
    model = PublicationRelation
    fk_name = 'from_publication'
    fields = ['rubric', 'to_publication',]
    extra = 1
    form = PublicationRelationInlineForm
    salmonella_fields = ('to_publication', )


#===========================================================================================
#
#===========================================================================================
class PublicationAdmin(SalmonellaMixin, AdminImageMixin, PlaceholderFieldAdmin):

    form = PublicationAdminForm

    save_on_top = True

    actions_selection_counter = True

    list_display = ('name', 'active', 'get_rubrics_count', 'date_added', 'last_modified', 'group_name', 'author', 'slug', )

    list_display_links = ('slug', 'name')

    list_filter = (RubricsTreeFilter, 'date_added', 'last_modified', 'active')

    search_fields = ['slug', 'name', 'sub_name', 'group__name', 'author']

    list_editable = ('active',)

    salmonella_fields = ('group', )

    class Media:
        js = [
                '/static/admin/js/jquery.treeview.js',
                '/static/admin/js/treeview_init.js',
                '/static/admin/js/publication_treeveiw_filter.js',
              ]
        css = {
            'all': [
                '/static/admin/css/changelist.css',
                '/static/publication_backbone/lib/font-awesome/css/font-awesome.min.css',
                '/static/admin/css/jquery.treeview.css',
                '/static/admin/css/style.css',
                ]
        }

    fieldsets = (
        (None, {
                'fields':
                    ('name', 'sub_name', 'slug', 'author', 'tags', 'active',)
               }),
        (None, {
                'fields':
                    ('comments_enabled', 'is_main', 'show_date',)
               }),
        (None, {
                'fields':
                    ('group', 'rubrics',)
               }),
        (None, {
                 'fields':
                    ('image', 'description', 'date_added',)
               }),
        (_("Contents"), {
            'fields': ('content',),
            'classes': ('plugin-holder',),
        }),
    )


    inlines = [PublicationCharacteristicOrMark_Inline, PublicationRelation_Inline, PublicationRelatedCategory_Inline, ]

    prepopulated_fields = {"slug": ("name",)}

    actions = [set_selected_rubrics, set_publicationgroup,  set_rubrics_by_attributes]


if not Publication in admin.site._registry:
    admin.site.register(Publication, PublicationAdmin)

