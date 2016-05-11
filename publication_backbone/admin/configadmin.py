#-*- coding: utf-8 -*-
import hashlib
from operator import itemgetter

from django.contrib import admin, messages
from django.contrib.admin.options import csrf_protect_m
from django.http import HttpResponseRedirect
from django.utils.formats import localize
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.utils.encoding import smart_bytes
from django.template.response import TemplateResponse
from django import VERSION
from constance.admin import ConstanceAdmin, ConstanceForm
from constance.admin import FIELDS

from publication_backbone.config import settings
from publication_backbone import conf as config

try:
    from django.conf.urls import patterns, url
except ImportError:  # Django < 1.4
    from django.conf.urls.defaults import patterns, url


class PublicationBackboneConstanceForm(ConstanceForm):

    def __init__(self, initial, *args, **kwargs):
        super(PublicationBackboneConstanceForm, self).__init__(*args, initial=initial, **kwargs)

        version_hash = hashlib.md5()

        for name, (default, help_text) in settings.CONFIG.items():
            config_type = type(default)
            if config_type not in FIELDS:
                raise ImproperlyConfigured(_("Constance doesn't support "
                                             "config values of the type "
                                             "%(config_type)s. Please fix "
                                             "the value of '%(name)s'.")
                                           % {'config_type': config_type,
                                              'name': name})
            field_class, kwargs = FIELDS[config_type]
            self.fields[name] = field_class(label=name, **kwargs)

            version_hash.update(smart_bytes(initial.get(name, '')))
        self.initial['version'] = version_hash.hexdigest()

    def save(self):
        for name in settings.CONFIG:
            setattr(config, name, self.cleaned_data[name])


class PublicationBackboneConfig(object):

    class Meta(object):
        app_label = 'publication_backbone'
        model_name = module_name = 'config'
        verbose_name_plural = _('Config')
        object_name = _('Config')
        abstract = False
        swapped = False

        def get_ordered_objects(self):
            return False

        def get_change_permission(self):
            return 'change_%s' % self.model_name

    _meta = Meta()



class PublicationBackboneConstanceAdmin(ConstanceAdmin):
    change_list_template = 'admin/constance/change_list.html'

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):

        # First load a mapping between config name and default value
        if not self.has_change_permission(request, None):
            raise PermissionDenied
        default_initial = ((name, default)
            for name, (default, help_text) in settings.CONFIG.items())
        # Then update the mapping with actually values from the backend
        #from constance import config
        initial = dict(default_initial,
            **dict(config._backend.mget(settings.CONFIG.keys())))

        form = PublicationBackboneConstanceForm(initial=initial)

        if request.method == 'POST':
            form = PublicationBackboneConstanceForm(data=request.POST, initial=initial)
            if form.is_valid():
                form.save()
                # In django 1.5 this can be replaced with self.message_user
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    _('Live settings updated successfully.'),
                )
                return HttpResponseRedirect('.')
        context = {
            'config_values': [],
            'title': _('PublicationBackbone config'),
            'app_label': PublicationBackboneConfig._meta.app_label,
            'opts': PublicationBackboneConfig._meta,
            'form': form,
            'media': self.media + form.media,
        }

        for name, (default, help_text) in settings.CONFIG.items():
            # First try to load the value from the actual backend
            value = initial.get(name)
            # Then if the returned value is None, get the default
            if value is None:
                value = getattr(config, name)
            context['config_values'].append({
                'name': name,
                'default': localize(default),
                'help_text': _(help_text),
                'value': localize(value),
                'modified': value != default,
                'form_field': form[name],
            })
        context['config_values'].sort(key=itemgetter('name'))

        request.current_app = self.admin_site.name
        # compatibility to be removed when 1.7 is deprecated
        extra = {'current_app': self.admin_site.name} if VERSION < (1, 8) else {}
        return TemplateResponse(request, self.change_list_template, context,
                                **extra)



admin.site.register([PublicationBackboneConfig], PublicationBackboneConstanceAdmin)