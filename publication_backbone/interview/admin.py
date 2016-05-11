from django.contrib import admin
from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import Interview, InterviewQuestion
from django.utils.translation import ugettext_lazy as _


class InterviewAdminForm(forms.ModelForm):
    final_text = forms.CharField(widget=CKEditorWidget(), label=_("Final text"), help_text=_('Interview final text'), required=False)
    class Meta:
        model = Interview


class InterviewQestionInline(admin.TabularInline):
    model = InterviewQuestion
    extra = 1


def is_up_to_date_flag(self):
    return self.is_up_to_date
is_up_to_date_flag.short_description =  _('Is up to date')
is_up_to_date_flag.boolean = True


class InterviewAdmin(admin.ModelAdmin):
    model = Interview
    form = InterviewAdminForm
    inlines = [InterviewQestionInline]
    list_display = ('name', is_up_to_date_flag, 'date_end')
    search_fields = ['name',]


admin.site.register(Interview, InterviewAdmin)