#-*- coding: utf-8 -*-
from django import forms
from django.contrib import admin, messages
from django.contrib.admin.options import csrf_protect_m
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from django.conf import settings
import os, shutil
from django.core.files import File
from django.core.management import call_command
from django_ace import AceWidget
from django.contrib.staticfiles.finders import AppDirectoriesFinder

try:
    from django.conf.urls import patterns, url
except ImportError:  # Django < 1.4
    from django.conf.urls.defaults import patterns, url


finder = AppDirectoriesFinder()

LESS_FILES = {
    'custom_less': finder.find('src/less/custom.less'),
}

if (not settings.DEBUG):
    for less_file in LESS_FILES:
        less_file_name = LESS_FILES.get(less_file)
        old_less_file_name = less_file_name + '.bak'
        if not os.access(old_less_file_name, os.R_OK):
            shutil.copy(less_file_name, old_less_file_name)


class StylesLessForm(forms.Form):
    custom_less = forms.CharField(
        widget=AceWidget(theme='xcode', mode='less', wordwrap=False, width="100%", height="500px", showprintmargin=True),
        label=_('Custom'),
        required=True
    )

    def save(self, initial):
        res = False
        for form_field in self.cleaned_data:
            if self.cleaned_data[form_field].encode("UTF-8") != initial[form_field]:
                f = open(LESS_FILES.get(form_field),'w+')
                less_file = File(f)
                less_source = self.cleaned_data[form_field].encode("UTF-8")
                less_file.write(less_source)
                f.close()
                res = True
        return res


class StylesAdmin(admin.ModelAdmin):

    class Media:
        js = [
                '/static/admin/js/collapsed_tabular_inlines.js',
                '/static/admin/js/list_filter_collapse.js',

              ]
        css = {
            'all': [
                '/static/admin/css/style.css',
                '/static/admin/css/changelist.css',
                '/static/admin/css/forms.css',
                ]
        }

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.module_name
        return patterns('',
            url(r'^$',
                self.admin_site.admin_view(self.changelist_view),
                name='%s_%s_changelist' % info),
            url(r'^$',
                self.admin_site.admin_view(self.changelist_view),
                name='%s_%s_add' % info),
        )

    def make_collectstatic(self, request):
        if (not settings.DEBUG):
            call_command('collectstatic', interactive=False, verbosity=0)
        else:
            messages.add_message(
                request,
                messages.INFO,
                _('Compile are not required into debug mode.'),
                )
        messages.add_message(
            request,
            messages.SUCCESS,
            _('Styles updated successfully.'),
            )
        return HttpResponseRedirect('.')

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        if not self.has_change_permission(request, None):
            raise PermissionDenied

        initial = {}
        for form_field in LESS_FILES:
            try:
                f = open(LESS_FILES.get(form_field),'r+')
                less_source = f.read()
                f.close()
            except:
                less_source = ''
            initial.__setitem__(form_field, less_source)

        default_less = {}
        for form_field in LESS_FILES:
            try:
                f = open(LESS_FILES.get(form_field)+'.bak','r+')
                less_source = f.read()
                f.close()
            except:
                less_source = ''
            default_less.__setitem__(form_field, less_source)

        styles_form = StylesLessForm(initial=initial)
        if request.method == 'POST':
            styles_form = StylesLessForm(request.POST)
            if '_proceed' in request.POST:
                if styles_form.is_valid():
                    if not styles_form.save(initial):
                        messages.add_message(
                            request,
                            messages.INFO,
                            _('Nothing has changed.'),
                            )
                    self.make_collectstatic(request)
        context = {
            'title': _('Styles editor'),
            'app_label': 'publication_backbone',
            'opts': Styles._meta,
            'styles_form': styles_form,
            'default_less': default_less,
            'media': self.media + styles_form.media,
        }
        context_instance = RequestContext(request,
                                          current_app=self.admin_site.name)
        return render_to_response('publication_backbone/admin/stylesadmin/styles_change.html',
                                  context, context_instance=context_instance, content_type='text/html; charset=UTF-8')

    def has_add_permission(self, *args, **kwargs):
        return False

    def has_delete_permission(self, *args, **kwargs):
        return False

    def has_change_permission(self, request, obj=None):
        return super(StylesAdmin, self).has_change_permission(request, obj)


class Styles(object):
    class Meta(object):
        app_label = 'publication_backbone'
        model_name = module_name = 'styles_editor'
        verbose_name_plural = _('styles')
        get_ordered_objects = lambda x: False
        abstract = False
        swapped = False
        object_name = _('styles')

        def get_change_permission(self):
            return 'change_%s' % self.model_name

    _meta = Meta()

admin.site.register([Styles], StylesAdmin)
