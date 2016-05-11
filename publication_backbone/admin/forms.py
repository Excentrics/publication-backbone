#-*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.contrib import admin
from django.forms import models
from mptt.forms import TreeNodeMultipleChoiceField, TreeNodeChoiceField

from publication_backbone.models import (
    Publication,
    Rubric,
    Category,
    BaseCategory,
    PublicationGroup,
    PublicationRelation,
)

from publication_backbone.forms_bases.mptt.forms import FullPathTreeNodeChoiceField

from ckeditor.widgets import CKEditorWidget
from salmonella.widgets import SalmonellaIdWidget
from publication_backbone.admin.widgets import RubricTreeWidget


#==============================================================================
# PublicationAdminForm
#==============================================================================
class PublicationAdminForm(forms.ModelForm):
    rubrics = forms.ModelMultipleChoiceField(queryset=Rubric.objects.active().exclude(system_flags=Rubric.system_flags.tagged_restriction),
                                          required=False, widget=RubricTreeWidget(), label=_("Rubrics"))

    class Meta:
        model = Publication


#==============================================================================
# CategoryAdminForm
#==============================================================================
class CategoryAdminForm(forms.ModelForm):
    rubrics = forms.ModelMultipleChoiceField(queryset=Rubric.objects.all(), #active(),
                                          required=False, widget=RubricTreeWidget(), label=_("Rubrics"))
    parent = TreeNodeChoiceField(queryset=BaseCategory.objects.all(),
                                          level_indicator=u'+--',
                                          #empty_label='-'*9,
                                          label=_('Parent'), required=False)
    class Meta:
        model = BaseCategory


#==============================================================================
# RubricAdminForm
#==============================================================================
class RubricAdminForm(forms.ModelForm):
    parent = TreeNodeChoiceField(queryset=Rubric.objects.all(),
                                          level_indicator=u'+--',
                                          label=_('Parent'), required=False)
    class Meta:
        model = Rubric

    def clean(self):
        cleaned_data = self.cleaned_data
        #if not cleaned_data.get("main_object"):
        #    raise forms.ValidationError("Closed for editing")
        try:
            result = super(RubricAdminForm, self).clean() # important- let admin do its work on data!
        except Rubric.EditNotAllowedError as e:
            raise forms.ValidationError(e)
        return result


#==============================================================================
# PublicationCharacteristicOrMarkInlineForm
#==============================================================================
class PublicationCharacteristicOrMarkInlineForm(models.ModelForm):
    rubric = FullPathTreeNodeChoiceField(queryset=Rubric.objects.attribute_is_characteristic_or_mark(),
                                          joiner=' / ',
                                          label=_('Characteristic or mark'))


#==============================================================================
# PublicationRelationInlineForm
#==============================================================================
class PublicationRelationInlineForm(models.ModelForm):
    rubric = FullPathTreeNodeChoiceField(queryset=Rubric.objects.attribute_is_relation(),
                                          joiner=' / ',
                                          label=_('Relation'))

    to_publication = forms.ModelChoiceField(queryset=Publication.objects.all(),
                                        widget=SalmonellaIdWidget(PublicationRelation._meta.get_field("to_publication").rel, admin.site),
                                        label=_('Target'))


#==============================================================================
# CategoryPublicationRelationInlineForm
#==============================================================================
class CategoryPublicationRelationInlineForm(models.ModelForm):
    rubric = FullPathTreeNodeChoiceField(queryset=Rubric.objects.attribute_is_relation(),
                                         required=False,
                                         joiner=' / ',
                                         label=_('Relation filter'))


#==============================================================================
# CategoryPromotionAdminForm
#==============================================================================
class CategoryPromotionAdminForm(forms.ModelForm):
    category = TreeNodeChoiceField(queryset=Category.objects.all(),
                                          level_indicator=u'+--',
                                          label=_("Category"))


#==============================================================================
# PublicationSelectRubricsAdminForm
#==============================================================================
class PublicationSelectRubricsAdminForm(forms.Form):
    rubrics_set = TreeNodeMultipleChoiceField(queryset=Rubric.objects.all(), level_indicator=u'+--', #empty_label='-'*9,
                                          required=False, label=_("Rubrics to set"), help_text=_(
        """Use "ctrl" key for choose multiple rubrics"""))
    rubrics_unset = TreeNodeMultipleChoiceField(queryset=Rubric.objects.all(), level_indicator=u'+--', #empty_label='-'*9,
                                          required=False, label=_("Rubrics to unset"), help_text=_(
        """Use "ctrl" key for choose multiple rubrics"""))

    def __init__(self, *args, **kwargs):
        super(PublicationSelectRubricsAdminForm, self).__init__(*args, **kwargs)

        # change a widget attribute:
        self.fields['rubrics_set'].widget.attrs["size"] = 40
        self.fields['rubrics_unset'].widget.attrs["size"] = 40


#==============================================================================
# PublicationSetDescriptionAdminForm
#==============================================================================
class PublicationSetDescriptionAdminForm(forms.Form):
    description = forms.CharField(widget=CKEditorWidget(), label=_('Description'), required=False)


#==============================================================================
# PublicationSelectGroupsAdminForm
#==============================================================================
class PublicationSelectGroupsAdminForm(forms.Form):

    group = forms.ModelChoiceField(queryset=PublicationGroup.objects.all(), widget=SalmonellaIdWidget(Publication._meta.get_field("group").rel, admin.site), label=_('Group'))


#==============================================================================
# PublicationSetEstimatedDeliveryAdminForm
#==============================================================================
class PublicationSetEstimatedDeliveryAdminForm(forms.Form):
    estimated_delivery = forms.CharField(label=_('estimated delivery'), required=False)


#==============================================================================
# MergeRubricsAdminForm
#==============================================================================
class MergeRubricsAdminForm(forms.Form):

    to_rubric = TreeNodeChoiceField(queryset=Rubric.objects.all(),
                                    level_indicator=u'+--',
                                    label=_("Destination rubric"), help_text=_(
        """Select destination rubric to merge"""))


#==============================================================================
# MakeRubricsByPublicationsAttributesAdminForm
#==============================================================================
class MakeRubricsByPublicationsAttributesAdminForm(forms.Form):
    pass