from django.contrib.admin import helpers
from django.template.response import TemplateResponse
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.util import quote, model_ngettext
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.core.management.base import CommandError

from publication_backbone.admin.forms import (
    PublicationSelectRubricsAdminForm,
    PublicationSetDescriptionAdminForm,
    PublicationSelectGroupsAdminForm,
    PublicationSetEstimatedDeliveryAdminForm,
    MergeRubricsAdminForm,
    MakeRubricsByPublicationsAttributesAdminForm,
)


def set_selected_rubrics(modeladmin, request, queryset):
    """
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label

    def format_callback(obj):
        opts = obj._meta
        admin_url = reverse('%s:%s_%s_change'
                            % (modeladmin.admin_site.name,
                               opts.app_label,
                               opts.object_name.lower()),
                            None, (quote(obj._get_pk_val()),))
        # Display a link to the admin page.
        return mark_safe(u'%s: <a href="%s">%s</a>' %
                         (escape(capfirst(opts.verbose_name)),
                          admin_url,
                          escape(obj)))

    def rubric_proceed(publication, rubrics_set, rubrics_unset):
        publication_rubrics = publication.rubrics.all()
        if rubrics_set and len(rubrics_set) != 0:
            for rubric in rubrics_set:
                if not rubric in publication_rubrics:
                    publication.rubrics.add(rubric)
        if rubrics_unset and len(rubrics_unset) != 0:
            for rubric in rubrics_unset:
                if rubric in publication_rubrics:
                    publication.rubrics.remove(rubric)
        publication.save()

    to_proceed = []
    for obj in queryset:
        to_proceed.append(format_callback(obj))

    if request.POST.get('post'):
        form = PublicationSelectRubricsAdminForm(request.POST)
        if form.is_valid():
            rubrics_set = form.cleaned_data['rubrics_set']
            rubrics_unset = form.cleaned_data['rubrics_unset']
            n = queryset.count()
            if n:
                for publication in queryset:
                    obj_display = force_unicode(obj)
                    modeladmin.log_change(request, obj, obj_display)
                    rubric_proceed(publication, rubrics_set, rubrics_unset)

                modeladmin.message_user(request, _("Successfully proceed %(count)d %(items)s.") % {
                    "count": n, "items": model_ngettext(modeladmin.opts, n)
                })
            # Return None to display the change list page again.
            return None

    if len(queryset) == 1:
        objects_name = force_unicode(opts.verbose_name)
    else:
        objects_name = force_unicode(opts.verbose_name_plural)

    form = PublicationSelectRubricsAdminForm()

    title = _("Are you sure?")
    context = {
        "title": title,
        'form': form,
        "objects_name": objects_name,
        "to_proceed": [to_proceed],
        'queryset': queryset,
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    }
    # Display the confirmation page
    return TemplateResponse(request, "publication_backbone/admin/actions/set_selected_rubrics.html",
                            context, current_app=modeladmin.admin_site.name)

set_selected_rubrics.short_description = _("Set or unset rubrics for selected %(verbose_name_plural)s")


def set_description(modeladmin, request, queryset):
    """
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label
    error_message = None
    def format_callback(obj):
        opts = obj._meta
        admin_url = reverse('%s:%s_%s_change'
                            % (modeladmin.admin_site.name,
                               opts.app_label,
                               opts.object_name.lower()),
                            None, (quote(obj._get_pk_val()),))
        # Display a link to the admin page.
        return mark_safe(u'%s: <a href="%s">%s</a>' %
                         (escape(capfirst(opts.verbose_name)),
                          admin_url,
                          escape(obj)))

    to_proceed = []
    for obj in queryset:
        to_proceed.append(format_callback(obj))

    if request.POST.get('post'):
        form = PublicationSetDescriptionAdminForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data['description'].strip()
            if description=='':
                description = None
            n = queryset.count()
            if n:
                for publication in queryset:
                    obj_display = force_unicode(obj)
                    modeladmin.log_change(request, obj, obj_display)
                    publication.description = description
                    publication.save()
                modeladmin.message_user(request, _("Successfully proceed %(count)d %(items)s.") % {
                    "count": n, "items": model_ngettext(modeladmin.opts, n)
                })
            # Return None to display the change list page again.
            return None

    if len(queryset) == 1:
        objects_name = force_unicode(opts.verbose_name)
    else:
        objects_name = force_unicode(opts.verbose_name_plural)

    form = PublicationSetDescriptionAdminForm()

    title = _("Are you sure?")
    context = {
        "title": title,
        'form': form,
        "objects_name": objects_name,
        "to_proceed": [to_proceed],
        'queryset': queryset,
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'error_message': error_message,
    }
    # Display the confirmation page
    return TemplateResponse(request, "publication_backbone/admin/actions/set_description.html",
                            context, current_app=modeladmin.admin_site.name)

set_description.short_description = _("Set description for selected %(verbose_name_plural)s")


def set_publicationgroup(modeladmin, request, queryset):
    """
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label
    error_message = None

    def format_callback(obj):
        opts = obj._meta
        admin_url = reverse('%s:%s_%s_change'
                            % (modeladmin.admin_site.name,
                               opts.app_label,
                               opts.object_name.lower()),
                            None, (quote(obj._get_pk_val()),))
        # Display a link to the admin page.
        return mark_safe(u'%s: <a href="%s">%s</a>' %
                         (escape(capfirst(opts.verbose_name)),
                          admin_url,
                          escape(obj)))

    to_proceed = []
    for obj in queryset:
        to_proceed.append(format_callback(obj))

    if request.POST.get('post'):

        form = PublicationSelectGroupsAdminForm(request.POST)
        if form.is_valid():
            group = form.cleaned_data['group']
            n = queryset.count()
            if n:
                for publication in queryset:
                    obj_display = force_unicode(obj)
                    modeladmin.log_change(request, obj, obj_display)
                    publication.group = group
                    publication.save()
                modeladmin.message_user(request, _("Successfully proceed %(count)d %(items)s.") % {
                    "count": n, "items": model_ngettext(modeladmin.opts, n)
                })
            # Return None to display the change list page again.
            return None

    if len(queryset) == 1:
        objects_name = force_unicode(opts.verbose_name)
    else:
        objects_name = force_unicode(opts.verbose_name_plural)

    form = PublicationSelectGroupsAdminForm()

    title = _("Are you sure?")
    context = {
        "title": title,
        'form': form,
        "objects_name": objects_name,
        "to_proceed": [to_proceed],
        'queryset': queryset,
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'error_message': error_message,
    }
    return TemplateResponse(request, "publication_backbone/admin/actions/set_group.html",
                            context, current_app=modeladmin.admin_site.name)

set_publicationgroup.short_description = _("Set group for selected %(verbose_name_plural)s")


def set_estimated_delivery(modeladmin, request, queryset):
    """
    Set estimated delivery
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label
    error_message = None

    def format_callback(obj):
        opts = obj._meta
        admin_url = reverse('%s:%s_%s_change'
                            % (modeladmin.admin_site.name,
                               opts.app_label,
                               opts.object_name.lower()),
                            None, (quote(obj._get_pk_val()),))
        # Display a link to the admin page.
        return mark_safe(u'%s: <a href="%s">%s</a>' %
                         (escape(capfirst(opts.verbose_name)),
                          admin_url,
                          escape(obj)))

    to_proceed = []
    for obj in queryset:
        to_proceed.append(format_callback(obj))

    if request.POST.get('post'):
        form = PublicationSetEstimatedDeliveryAdminForm(request.POST)
        if form.is_valid():
            estimated_delivery = form.cleaned_data['estimated_delivery'].strip()
            if estimated_delivery == '':
                estimated_delivery = None
            n = queryset.count()
            if n:
                for publication in queryset:
                    obj_display = force_unicode(obj)
                    modeladmin.log_change(request, obj, obj_display)
                    publication.estimated_delivery = estimated_delivery
                    publication.save()
                modeladmin.message_user(request, _("Successfully proceed %(count)d %(items)s.") % {
                    "count": n, "items": model_ngettext(modeladmin.opts, n)
                })
            # Return None to display the change list page again.
            return None

    if len(queryset) == 1:
        objects_name = force_unicode(opts.verbose_name)
    else:
        objects_name = force_unicode(opts.verbose_name_plural)

    form = PublicationSetEstimatedDeliveryAdminForm()

    title = _("Are you sure?")
    context = {
        "title": title,
        'form': form,
        "objects_name": objects_name,
        "to_proceed": [to_proceed],
        'queryset': queryset,
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'error_message': error_message,
    }
    return TemplateResponse(request, "publication_backbone/admin/actions/set_estimated_delivery.html",
                            context, current_app=modeladmin.admin_site.name)

set_estimated_delivery.short_description = _("Set estimated delivery for selected %(verbose_name_plural)s")


def merge_rubrics(modeladmin, request, queryset):
    """
    Merge rubrics
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label
    error_message = None

    # Check that the user has delete and change permission for the actual model
    if not (modeladmin.has_delete_permission(request) and modeladmin.has_change_permission(request)):
        raise PermissionDenied

    def format_callback(obj):
        opts = obj._meta
        admin_url = reverse('%s:%s_%s_change'
                            % (modeladmin.admin_site.name,
                               opts.app_label,
                               opts.object_name.lower()),
                            None, (quote(obj._get_pk_val()),))
        # Display a link to the admin page.
        return mark_safe(u'%s: <a href="%s">%s</a>' %
                         (escape(capfirst(opts.verbose_name)),
                          admin_url,
                          escape(obj)))
    to_proceed = []
    for obj in queryset:
        to_proceed.append(format_callback(obj))

    if request.POST.get('post'):
        form = MergeRubricsAdminForm(request.POST)
        if form.is_valid():
            to_rubric = form.cleaned_data['to_rubric']
            n = queryset.count()
            if n:
                try:
                    for from_rubric in queryset:
                        call_command('merge_rubrics', to_id=to_rubric.id, from_id=from_rubric.id)

                    to_rubric_display = force_unicode(to_rubric)
                    modeladmin.log_change(request, to_rubric, to_rubric_display)

                    modeladmin.message_user(request, _("Successfully proceed %(count)d %(items)s.") % {
                        "count": n, "items": model_ngettext(modeladmin.opts, n)
                    })
                    return None
                except CommandError as e:
                    error_message = force_unicode(e)
    else:
        form = MergeRubricsAdminForm()

    context = {
        "title": _("Merging rubrics"),
        'form': form,
        "objects_name": force_unicode(opts.verbose_name) if len(queryset) else force_unicode(opts.verbose_name_plural),
        "to_proceed": [to_proceed],
        'queryset': queryset,
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'error_message': error_message,
    }
    return TemplateResponse(request, "publication_backbone/admin/actions/merge_rubrics.html",
                            context, current_app=modeladmin.admin_site.name)

merge_rubrics.short_description = _("Merge selected %(verbose_name_plural)s with %(verbose_name)s")


def make_rubrics_by_publications_attributes(modeladmin, request, queryset):
    """
    Make sub rubrics structure by additional publications attributes.
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label
    error_message = None

    # Check that the user has delete and change permission for the actual model
    if not (modeladmin.has_delete_permission(request) and modeladmin.has_change_permission(request)):
        raise PermissionDenied

    def format_callback(obj):
        opts = obj._meta
        admin_url = reverse('%s:%s_%s_change'
                            % (modeladmin.admin_site.name,
                               opts.app_label,
                               opts.object_name.lower()),
                            None, (quote(obj._get_pk_val()),))
        # Display a link to the admin page.
        return mark_safe(u'%s: <a href="%s">%s</a>' %
                         (escape(capfirst(opts.verbose_name)),
                          admin_url,
                          escape(obj)))
    to_proceed = []
    for obj in queryset:
        to_proceed.append(format_callback(obj))

    if request.POST.get('post'):
        form = MakeRubricsByPublicationsAttributesAdminForm(request.POST)
        if form.is_valid():
            n = queryset.count()
            if n:
                try:
                    for target_rubric in queryset:
                        call_command('make_rubrics_by_publications_attributes', target_id=target_rubric.id)
                        #target_rubric_display = force_unicode(target_rubric)
                        #modeladmin.log_change(request, target_rubric, target_rubric_display)
                    modeladmin.message_user(request, _("Successfully proceed %(count)d %(items)s.") % {
                        "count": n, "items": model_ngettext(modeladmin.opts, n)
                    })
                    return None
                except CommandError as e:
                    error_message = force_unicode(e)
    else:
        form = MakeRubricsByPublicationsAttributesAdminForm()

    context = {
        "title": _("Making sub rubrics structure by additional publications attributes"),
        'form': form,
        "objects_name": force_unicode(opts.verbose_name) if len(queryset) else force_unicode(opts.verbose_name_plural),
        "to_proceed": [to_proceed],
        'queryset': queryset,
        "opts": opts,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'error_message': error_message,
    }
    return TemplateResponse(request, "publication_backbone/admin/actions/make_rubrics_by_publications_attibutes.html",
                            context, current_app=modeladmin.admin_site.name)

make_rubrics_by_publications_attributes.short_description = _("Make sub rubrics structure by additional publications attributes")


def set_rubrics_by_attributes(modeladmin, request, queryset):
    """
    Set rubrics to publication by additional attributes
    """
    try:
        for publication in queryset:
            call_command('set_publication_rubrics_by_attributes', publication_id=publication.pk)

        modeladmin.message_user(request, _("Set rubrics from attributes for %s publications") % queryset.count())

    except CommandError as e:
        from django.contrib import messages
        modeladmin.message_user(request, force_unicode(e), level=messages.ERROR)


set_rubrics_by_attributes.short_description = _("Set rubrics to publication by additional attributes")