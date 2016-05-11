#-*- coding: utf-8 -*-
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
from django_mptt_admin.admin import DjangoMpttAdmin


class PolymorphicMPTTChildModelAdmin(PolymorphicChildModelAdmin):
    """ Base admin class for all child models """
    pass


class PolymorphicMPTTParentModelAdmin(PolymorphicParentModelAdmin, DjangoMpttAdmin):
    """ The parent model admin """

    def __init__(self, *args, **kwargs):
        self._change_list_template = []
        super(PolymorphicMPTTParentModelAdmin, self).__init__(*args, **kwargs)

    @property
    def change_list_template(self):
        opts = self.model._meta
        app_label = opts.app_label
        # Pass the base options
        base_opts = self.base_model._meta
        base_app_label = base_opts.app_label
        change_list_template = [
            "admin/%s/%s/django_mptt_admin/grid_view.html" % (app_label, opts.object_name.lower()),
            "admin/%s/django_mptt_admin/grid_view.html" % app_label,
            # Added base class:
            "admin/%s/%s/django_mptt_admin/grid_view.html" % (base_app_label, base_opts.object_name.lower()),
            "admin/%s/django_mptt_admin/grid_view.html" % base_app_label,
            "django_mptt_admin/grid_view.html"
        ]
        return self._change_list_template + change_list_template + super(PolymorphicMPTTParentModelAdmin, self).change_list_template

    @change_list_template.setter
    def change_list_template(self, value):
        self._change_list_template = value

