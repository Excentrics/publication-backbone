#-*- coding: utf-8 -*-
import os
from django.template.response import TemplateResponse
from django.contrib.admin import ModelAdmin, helpers
from django.contrib.admin.util import unquote
from django.conf.urls import patterns, url
from django.utils.encoding import force_unicode, force_text
from django.utils.translation import ugettext as _
from django.utils.html import escape
from django.forms.models import model_to_dict
from django.forms.formsets import all_valid
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.datastructures import MultiValueDict
from django.utils.safestring import mark_safe
from django.core.files.base import ContentFile
from django.http import Http404, HttpResponseRedirect
from django.contrib.admin.helpers import AdminForm, AdminErrorList
from django.forms.models import modelform_factory
from django.contrib.admin.util import flatten_fieldsets
from functools import partial
from bitfield.forms import BitFieldCheckboxSelectMultiple
from publication_backbone.models import Category, Publication, PublicationCharacteristicOrMark


__all__ = 'ChangeTypeModelAdmin',

def rubric_model_to_dict(obj, fields=None, exclude=None, ct_id=None):
    """
    Returns a dict containing the data in ``instance`` suitable for passing as
    a Form's ``initial`` keyword argument.

    ``fields`` is an optional list of field names. If provided, only the named
    fields will be included in the returned dict.

    ``exclude`` is an optional list of field names. If provided, the named
    fields will be excluded from the returned dict, even if they are listed in
    the ``fields`` argument.
    """
    # avoid a circular import
    from django.db.models.fields.related import ManyToManyField
    opts = obj._meta
    data = {}
    for f in opts.fields + opts.many_to_many:
        if not f.editable:
            continue
        if fields and not f.name in fields:
            continue
        if exclude and f.name in exclude:
            continue
        if isinstance(f, ManyToManyField):
            # If the object doesn't have a primary key yet, just use an empty
            # list for its m2m fields. Calling f.value_from_object will raise
            # an exception.
            if obj.pk is None:
                data[f.name] = []
            else:
                # MultipleChoiceWidget needs a list of pks, not object instances.
                data[f.name] = list(f.value_from_object(obj).values_list('pk', flat=True))
        else:
            data[f.name] = f.value_from_object(obj)
        if not ct_id is None:
            data["polymorphic_ctype_id"] = ct_id
    return data


class ChangeTypeModelAdmin(ModelAdmin):

    change_type_verbose_name = _('Change type')
    change_form_template = 'admin/model_change_type/change_form.html'

    model_class = None
    model_form = None

    class Media:
        css = {
            'all': [
                '/static/publication_backbone/admin/css/rubricator_child_admin_style.css',
                ]
        }
    #
    #  compose change type button link for form
    #
    def change_type_link(self, changetype_model):
        '''
        Method to be used on `list_display`, renders a link to clone model
        '''
        url = reverse('admin:{0}_{1}_change_type'.format(changetype_model._meta.app_label,
                                                   changetype_model._meta.module_name),
                      args=(changetype_model._get_pk_val(),),
                      current_app=self.admin_site.name)
        return '<a href="{0}">{1}</a>'.format(url, self.change_type_verbose_name)

    change_type_link.short_description = change_type_verbose_name  # not overridable by subclass
    change_type_link.allow_tags = True

    #
    #  compose urls for change type view
    #
    def get_urls(self):
        url_name = '{0}_{1}_change_type'.format(
            self.model._meta.app_label,
            self.model._meta.module_name)   # NOTE: Django 1.5 uses model_name here
        new_urlpatterns = patterns('',
            url(r'^(.+)/change_type/$',
                self.admin_site.admin_view(self.change_type),
                name=url_name),
        )
        original_urlpatterns = super(ChangeTypeModelAdmin, self).get_urls()
        return new_urlpatterns + original_urlpatterns

    def get_form(self, request, obj=None, **kwargs):
        """
        Returns a Form class for use in the admin change type view. This is used by
        add_view and change_view.
        """
        if self.declared_fieldsets:
            fields = flatten_fieldsets(self.declared_fieldsets)
        else:
            fields = None
        if self.exclude is None:
            exclude = []
        else:
            exclude = list(self.exclude)
        exclude.extend(self.get_readonly_fields(request, obj))
        if self.exclude is None and hasattr(self.form, '_meta') and self.form._meta.exclude:
            # Take the custom ModelForm's Meta.exclude into account only if the
            # ModelAdmin doesn't define its own.
            exclude.extend(self.form._meta.exclude)
        # if exclude is an empty list we pass None to be consistant with the
        # default on modelform_factory
        exclude = exclude or None
        defaults = {
            "form": self.form,
            "fields": fields,
            "exclude": exclude,
            "formfield_callback": partial(self.formfield_for_dbfield, request=request),
            "widgets": {"system_flags": BitFieldCheckboxSelectMultiple}
        }
        defaults.update(kwargs)
        try:
            the_model = self.model_class
            if the_model is None:
                the_model = self.model
        except:
            the_model = self.model
        return modelform_factory(the_model, **defaults)

    #
    #  override admin form method change_view. add new button on form view
    #
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context.update({
            'change_type_verbose_name': self.change_type_verbose_name,
            'include_change_type_link': True,
        })
        return super(ChangeTypeModelAdmin, self).change_view(request, object_id, form_url, extra_context)

    #
    #  display a choice form to select which rubric type add
    #
    def add_type_view(self, request, form_url=''):
        # prepare query string
        extra_qs = ''
        if request.META['QUERY_STRING']:
            extra_qs = '&' + request.META['QUERY_STRING']

        # remove current type choice
        choices = self.get_child_type_choices(request, 'add')
        #obj = self.get_object(request, unquote(object_id))
        #if obj is None:
        #    raise Http404(_('object with primary key {key} does not exist.'.format(key=repr(escape(object_id)))))

        #ctype_id = obj.polymorphic_ctype_id
        #choices = [x for x in all_choices if x[0]!= ctype_id]

        if len(choices) == 1:
            return HttpResponseRedirect('?ct_id={0}{1}'.format(choices[0][0], extra_qs))

        # make form for choose
        form = self.add_type_form(
            data=request.POST if request.method == 'POST' else None,
            initial={'ct_id': choices[0][0]}
        )
        form.fields['ct_id'].choices = choices

        # redirect if form is valid
        if form.is_valid():
            return HttpResponseRedirect('?ct_id={0}{1}'.format(form.cleaned_data['ct_id'], extra_qs))

        # compose adminform for view
        fieldsets = ((None, {'fields': ('ct_id',)}),)
        adminForm = AdminForm(form, fieldsets, {}, model_admin=self)
        media = self.media + adminForm.media
        opts = self.model._meta

        # prepare context and render form
        context = {
            'title': _('Change type'),
            'original': _('Change type'),
            'adminform': adminForm,
            'media': mark_safe(media),
            'errors': AdminErrorList(form, ()),
            'app_label': opts.app_label,
            'verbose_name': self.change_type_verbose_name,
        }
        return self.render_change_form(request, context, form_url)

    #
    #  render for change type view
    #
    def render_change_type_form(self, request, context, add=False, change=False, form_url='', obj=None):
        opts = self.model._meta
        app_label = opts.app_label
        context.update({
            'add': add,
            'change': change,
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request, obj),
            'has_delete_permission': self.has_delete_permission(request, obj),
            'has_file_field': True,
            'has_absolute_url': hasattr(self.model, 'get_absolute_url'),
            'form_url': form_url,
            'opts': opts,
            'content_type_id': ContentType.objects.get_for_model(self.model).id,
            'save_as': self.save_as,
            'save_on_top': self.save_on_top,
        })
        if add and self.add_form_template is not None:
            form_template = self.add_form_template
        else:
            form_template = self.change_form_template

        return TemplateResponse(request, form_template or [
            "admin/%s/%s/change_form.html" % (app_label, opts.object_name.lower()),
            "admin/%s/change_form.html" % app_label,
            "admin/change_form.html"
        ], context, current_app=self.admin_site.name)

    #
    #   main view. if not present content type then call select type form view
    #   else call change_type_view
    #
    def change_type(self, request, object_id, form_url='', extra_context=None):
        ct_id = int(request.GET.get('ct_id', 0))
        if not ct_id:
            # select type view
            return self.add_type_view(request)
        else:
            # change type view (GET, POST)
            return self.change_type_view(request, object_id, form_url='', extra_context=None,  ct_id=ct_id)

    #
    #  change type view. proceed POST and GET requests. if it 'GET' then prepare copy of original rubric, set
    #  right rubric type and render form object change. if it 'POST' then save new rubric, set it in publications
    #  and category and after save do delete old rubric object.
    #
    def change_type_view(self, request, object_id, form_url='', extra_context=None, ct_id=None):

        opts = self.model._meta
        # validate permission
        if not self.has_add_permission(request):
            raise PermissionDenied

        # get rubric for change type or raise error 404
        original_obj = self.get_object(request, unquote(object_id))
        if original_obj is None:
            raise Http404(_('{name} object with primary key {key} does not exist.'.format(
                name=force_unicode(opts.verbose_name),
                key=repr(escape(object_id))
            )))
        # get new content type for rubric or raise error 404
        try:
            ct = ContentType.objects.get_for_id(ct_id)
        except ContentType.DoesNotExist as e:
            raise Http404(e)

        # get new model class or raise error 404
        self.model_class = ct.model_class()
        if not self.model_class:
            raise Http404("No model found for '{0}.{1}'.".format(*ct.natural_key()))

        if original_obj.system_flags.change_subclass_restriction:
            raise ValidationError(original_obj.system_flags.get_label('change_subclass_restriction'))


        # set new model meta for admin interface
        opts = self.model_class._meta

        # compose model form from original object for transfer to new object
        ModelForm = self.get_form(request)

        formsets = []
        inline_instances = self.get_inline_instances(request)

        if request.method == 'POST':
            # method POST
            files_data = MultiValueDict()
            for field in [f for f in original_obj._meta.fields if isinstance(f, models.FileField)]:
                f = getattr(original_obj, field.name)
                if f:
                    tmp_file = ContentFile(f.read(), os.path.basename(f.name))
                    files_data.update(**{ field.name: tmp_file })

            for rf in [rel.field for rel in original_obj._meta.get_all_related_objects()
                      if isinstance(rel.field, models.ForeignKey) and rel.field.rel.related_name]:
                related_name = rf.rel.related_name
                related = getattr(original_obj, related_name)
                i = 0
                for obj in related.all():
                    for field in [f for f in obj._meta.fields if isinstance(f, models.FileField)]:
                        f = getattr(obj, field.name)
                        if f:
                            tmp_file = ContentFile(f.read(), os.path.basename(f.name))
                            files_data.update(**{ u'%s-%s-%s' % (related_name, i, field.name): tmp_file })
                        i += 1

            files_data.update(request.FILES)

            self.model_form = ModelForm(request.POST, files_data)
            if self.model_form.is_valid():
                new_object = self.save_form(request, self.model_form, change=False)
                form_validated = True
            else:
                new_object = self.model_class()
                form_validated = False

            prefixes = {}
            for FormSet, inline in zip(self.get_formsets(request), inline_instances):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1 or not prefix:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])

                formset = FormSet(data=request.POST, files=files_data,
                                  instance=new_object,
                                  save_as_new="_saveasnew" in request.POST,
                                  prefix=prefix)
                formsets.append(formset)

            if all_valid(formsets) and form_validated:
                original_obj.slug = 'old.' + original_obj.slug
                original_obj.path = 'old/' + original_obj.path
                original_obj.save(force_update=True)
                self.save_model(request, new_object, self.model_form, False) # save
                self.save_related(request, self.model_form, formsets, False)
                new_object.move_to(target=original_obj, position='left')

                self.log_change(request, new_object.get_base_instance(), _("Change %s type") % force_text(original_obj))

                # Update related rubrics
                child_of_original_rubric = original_obj.get_children()
                for child_rubric in child_of_original_rubric:
                    new_object = self.model_class.objects.get(pk=new_object.id)
                    child_rubric.move_to(new_object, 'last-child')
                    child_rubric.save()

                original_obj = self.model.objects.get(pk=original_obj.id)

                # Update related publications
                Publication.rubrics.through.objects.filter(rubric__exact=original_obj.id).update(rubric=new_object.id)

                # Update related publication attributes
                PublicationCharacteristicOrMark.objects.filter(rubric__exact=original_obj.id).update(rubric=new_object.id)

                # Update related categories
                Category.rubrics.through.objects.filter(rubric__exact=original_obj.id).update(rubric=new_object.id)

                original_obj.delete()

                return self.response_add(request, new_object)
        else:
            initial = rubric_model_to_dict(original_obj, ct_id=ct_id)
            self.model_form = ModelForm(initial=initial)
            prefixes = {}
            for FormSet, inline in zip(self.get_formsets(request), inline_instances):
                prefix = FormSet.get_default_prefix()
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
                if prefixes[prefix] != 1 or not prefix:
                    prefix = "%s-%s" % (prefix, prefixes[prefix])
                initial = []
                queryset = inline.queryset(request).filter(
                    **{FormSet.fk.name: original_obj})
                for obj in queryset:
                    initial.append(model_to_dict(obj, exclude=[obj._meta.pk.name,
                                                               FormSet.fk.name]))
                formset = FormSet(prefix=prefix, initial=initial)
                # since there is no way to customize the `extra` in the constructor,
                # construct the forms again...
                # most of this view is a hack, but this is the ugliest one
                formset.extra = len(initial) + formset.extra
                formset._construct_forms()
                formsets.append(formset)

        admin_form = helpers.AdminForm(
            self.model_form,
            list(self.get_fieldsets(request)),
            self.get_prepopulated_fields(request),
            self.get_readonly_fields(request)
        )
        media = self.media + admin_form.media

        inline_admin_formsets = []
        for inline, formset in zip(inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request, original_obj))
            readonly = list(inline.get_readonly_fields(request, original_obj))
            prepopulated = dict(inline.get_prepopulated_fields(request, original_obj))
            inline_admin_formset = InlineAdminFormSetFakeOriginal(inline, formset,
                fieldsets, prepopulated, readonly, model_admin=self)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media

        title = u'{0} {1}'.format(self.change_type_verbose_name, opts.verbose_name)
        context = {
            'title': title,
            'original': title,
            'adminform': admin_form,
            'is_popup': "_popup" in request.REQUEST,
            'show_delete': False,
            'media': media,
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(self.model_form, formsets),
            'app_label': opts.app_label,
        }

        context.update(extra_context or {})
        return self.render_change_type_form(request,
            context,
            form_url=form_url,
        )

class InlineAdminFormSetFakeOriginal(helpers.InlineAdminFormSet):

    def __iter__(self):
        # the template requires the AdminInlineForm to have an `original`
        # attribute, which is the model instance, in order to display the
        # 'Delete' checkbox
        # we don't have `original` because we are just providing initial
        # data to the form, so we attach a "fake original" (something that
        # evaluates to True) to fool the template and make is display
        # the 'Delete' checkbox
        # needless to say this is a terrible hack and will break in future
        # django versions :)
        for inline_form in super(InlineAdminFormSetFakeOriginal, self).__iter__():
            if inline_form.form.initial:
                inline_form.original = True
            yield inline_form
