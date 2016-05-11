#-*- coding: utf-8 -*-
import os
from django import forms
from django.contrib import admin, messages
from django.contrib.admin.options import csrf_protect_m
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from django.conf import settings
from django.core.files import File
from django_ace import AceWidget
from django.template.loaders.app_directories import Loader
from django.template.base import TemplateDoesNotExist
try:
    from django.conf.urls import patterns, url
except ImportError:  # Django < 1.4
    from django.conf.urls.defaults import patterns, url


template_loader = Loader()
try:
    PUBLICATION_DEFAULT_TEMPLATE_SOURCE = template_loader.load_template_source('publication_backbone/default_publication_detail.html')[0]
except TemplateDoesNotExist:
    PUBLICATION_DEFAULT_TEMPLATE_SOURCE = u''

PUBLICATION_DETAIL_TEMPLATE = os.path.join(settings.PROJECT_DIR, 'templates/publication_backbone/publication_detail.html')


class PublicationDetailTemplateForm(forms.Form):
    publication_detail_template_source = forms.CharField(
        widget=AceWidget(theme='xcode', mode='snippets', wordwrap=False, width="100%", height="480px", showprintmargin=True),
        label=_('Publication detail template'),
        required=True
    )

    def save(self, initial):

        res = False

        if self.cleaned_data['publication_detail_template_source'].encode("UTF-8") != PUBLICATION_DEFAULT_TEMPLATE_SOURCE.encode("UTF-8"):
            if self.cleaned_data['publication_detail_template_source'].encode("UTF-8") != initial['publication_detail_template_source']:
                root = os.path.dirname(PUBLICATION_DETAIL_TEMPLATE)
                if not os.path.isdir(root):
                    os.makedirs(root)
                try:
                    f = open(PUBLICATION_DETAIL_TEMPLATE,'w+')
                    publication_detail_template_file = File(f)
                    publication_detail_template_source = self.cleaned_data['publication_detail_template_source'].encode("UTF-8")
                    publication_detail_template_file.write(publication_detail_template_source)
                    f.close()
                    res = True
                except:
                    raise PermissionDenied
        else:
            root = os.path.dirname(PUBLICATION_DETAIL_TEMPLATE)
            if os.access(PUBLICATION_DETAIL_TEMPLATE, os.W_OK):
                os.remove(PUBLICATION_DETAIL_TEMPLATE)
            if os.path.isdir(root) and not os.listdir(root):
                os.rmdir(root)
        return res


class PublicationDetailTemplateAdmin(admin.ModelAdmin):

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

    def load_publication_detail_template_source(self, request):
        if os.access(PUBLICATION_DETAIL_TEMPLATE, os.W_OK):
            try:
                f = open(PUBLICATION_DETAIL_TEMPLATE,'r+')
                publication_detail_template_source = f.read()
                f.close()
            except:
                raise PermissionDenied
        else:
            messages.add_message(
                request,
                messages.ERROR,
                _('Error! Permission denied!'),
                )
            return HttpResponseRedirect('..')
        return publication_detail_template_source

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        if not self.has_change_permission(request, None):
            raise PermissionDenied

        if os.path.isfile(PUBLICATION_DETAIL_TEMPLATE):
            publication_detail_template_source = self.load_publication_detail_template_source(request)
        else:
            publication_detail_template_source = PUBLICATION_DEFAULT_TEMPLATE_SOURCE

        initial = {
            'publication_detail_template_source': publication_detail_template_source,
            }

        publication_detail_template_form = PublicationDetailTemplateForm(initial=initial)
        if request.method == 'POST':
            if '_proceed' in request.POST:
                publication_detail_template_form = PublicationDetailTemplateForm(request.POST)
                if publication_detail_template_form.is_valid():
                    if publication_detail_template_form.save(initial):
                        messages.add_message(
                            request,
                            messages.INFO,
                            _('Success. Publication template was saved.'),
                            )
                        return HttpResponseRedirect('.')
                    else:
                        messages.add_message(
                            request,
                            messages.INFO,
                            _('Nothing has changed.'),
                            )
                        return HttpResponseRedirect('.')

        context = {
            'title': _('Publication detail template editor'),
            'app_label': 'publication_backbone',
            'opts': PublicationDetailTemplate._meta,
            'styles_form': publication_detail_template_form,
            'default_publication_detail': PUBLICATION_DEFAULT_TEMPLATE_SOURCE,
            'media': self.media + publication_detail_template_form.media,
        }
        context_instance = RequestContext(request,
                                          current_app=self.admin_site.name)
        return render_to_response('publication_backbone/admin/templatesadmin/publication_detail_change.html',
                                  context, context_instance=context_instance, content_type='text/html; charset=UTF-8')

    def has_add_permission(self, *args, **kwargs):
        return False

    def has_delete_permission(self, *args, **kwargs):
        return False

    def has_change_permission(self, request, obj=None):
        return super(PublicationDetailTemplateAdmin, self).has_change_permission(request, obj)


class PublicationDetailTemplate(object):
    class Meta(object):
        app_label = 'publication_backbone'
        model_name = module_name = 'publication_detail_template_editor'
        verbose_name_plural = _('Publication detail template')
        get_ordered_objects = lambda x: False
        abstract = False
        swapped = False
        object_name = _('Publication detail template')

        def get_change_permission(self):
            return 'change_%s' % self.model_name

    _meta = Meta()

admin.site.register([PublicationDetailTemplate], PublicationDetailTemplateAdmin)