from django.contrib import admin
from django import forms
from ckeditor.widgets import CKEditorWidget
from django.utils.translation import ugettext_lazy as _

from .models import Quiz, QuizResult


class QuizAdminForm(forms.ModelForm):
    final_text = forms.CharField(widget=CKEditorWidget(), label=_("Final text"), help_text=_('Result final text'), required=False)
    class Meta:
        model = Quiz


class QuizResultInline(admin.TabularInline):
    model = QuizResult
    extra = 1


class QuizAdmin(admin.ModelAdmin):
    model = Quiz
    form = QuizAdminForm
    inlines = [QuizResultInline]
    list_display = ('name',)
    search_fields = ['name',]


admin.site.register(Quiz, QuizAdmin)