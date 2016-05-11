#-*- coding: utf-8 -*-
import json
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import FormMixin
from django.views.generic.list import MultipleObjectMixin
from django.views.generic.detail import SingleObjectMixin

from publication_backbone.views.utils import coerce_put_post


#==============================================================================
# FormSingleObjectMixin
#==============================================================================
class FormSingleObjectMixin(SingleObjectMixin, FormMixin):
    """
    A mixin that processes a form on POST for single object view.
    """
    action = None

    def dispatch(self, request, *args, **kwargs):
        """
        Submitting form works only for "GET" and "POST".
        If `action` is defined use it dispatch request to the right method.
        """

        coerce_put_post(request)

        if not self.action:
            return super(FormSingleObjectMixin, self).dispatch(request, *args,
                **kwargs)
        if self.action in self.http_method_names:

            if self.action == 'put' and not hasattr(request, 'PUT'):
                request.PUT = request.POST

            handler = getattr(self, self.action, self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        self.request = request
        self.args = args
        self.kwargs = kwargs
        return handler(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        return self.render_to_response(self.get_context_data(form=form, object=self.object))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            return self.form_valid(form, self.object)
        else:
            return self.form_invalid(form, self.object)

    # PUT is a valid HTTP verb for creating (with a known URL) or editing an
    # object, note that browsers only support POST for now.
    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def form_valid(self, form, object):
        if self.success_url:
            return HttpResponseRedirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form, object=object))

    def form_invalid(self, form, object):
        return self.render_to_response(self.get_context_data(form=form, object=object))


#==============================================================================
# FormMultipleObjectMixin
#==============================================================================
class FormMultipleObjectMixin(MultipleObjectMixin, FormMixin):
    """
    A mixin that processes a form on POST for multiple object view.
    """
    action = None

    def dispatch(self, request, *args, **kwargs):
        """
        Submitting form works only for "GET" and "POST".
        If `action` is defined use it dispatch request to the right method.
        """

        coerce_put_post(request)

        if not self.action:
            return super(FormMultipleObjectMixin, self).dispatch(request, *args,
                **kwargs)
        if self.action in self.http_method_names:

            if self.action == 'put' and not hasattr(request, 'PUT'):
                request.PUT = request.POST

            handler = getattr(self, self.action, self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        self.request = request
        self.args = args
        self.kwargs = kwargs
        return handler(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_object_list()

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        return self.render_to_response(self.get_context_data(form=form, object_list=self.object_list))

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_object_list()

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            return self.form_valid(form, self.object_list)
        else:
            return self.form_invalid(form, self.object_list)

    # PUT is a valid HTTP verb for creating (with a known URL) or editing an
    # object, note that browsers only support POST for now.
    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def form_valid(self, form, object_list):
        if self.success_url:
            return HttpResponseRedirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form, object_list=object_list))

    def form_invalid(self, form, object_list):
        return self.render_to_response(self.get_context_data(form=form, object_list=object_list))

    def get_object_list(self):
        object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()
        if not allow_empty and len(object_list) == 0:
            raise Http404(_(u"Empty list and '%(class_name)s.allow_empty' is False.")
                            % {'class_name': self.__class__.__name__})
        return object_list



#==============================================================================
# JSONResponseMixin
#=============================================================================
class JSONResponseMixin(object):
    """
    A mixin that can be used to render a JSON response.
    """
    response_class = HttpResponse

    def render_to_response(self, context, response_class=None, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        if not response_class:
           response_class = self.response_class
        response_kwargs['content_type'] = 'application/json'
        return response_class(
            self.convert_context_to_json(context),
            **response_kwargs
        )

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return json.dumps(context)


#==============================================================================
# JSONSingleObjectTemplateResponseMixin
#=============================================================================
class JSONSingleObjectTemplateResponseMixin(TemplateResponseMixin):
    """
    A mixin that can be used to render a templated JSON response.
    """
    json_template_name_field = None
    json_template_name_suffix = '_detail'

    def get_json_template_names(self):
        """
        Return a list of template names to be used for the request. Must return
        a list. May not be called if get_template is overridden.
        """
        try:
            names = super(JSONSingleObjectTemplateResponseMixin, self).get_json_template_names()
        except (ImproperlyConfigured, AttributeError):
            # 'super' object has no attribute 'get_json_template_names'
            # or
            # If template_name isn't specified, it's not a problem --
            # we just start with an empty list.
            names = []

        # If self.template_name_field is set, grab the value of the field
        # of that name from the object; this is the most specific template
        # name, if given.
        if self.object and self.json_template_name_field:
            name = getattr(self.object, self.json_template_name_field, None)
            if name:
                names.insert(0, name)

        # The least-specific option is the default <app>/<model>_detail.json;
        # only use this if the object in question is a model.
        if hasattr(self.object, '_meta'):
            names.append("%s/%s%s.json" % (
                self.object._meta.app_label,
                self.object._meta.object_name.lower(),
                self.json_template_name_suffix
            ))
        elif hasattr(self, 'model') and hasattr(self.model, '_meta'):
            names.append("%s/%s%s.json" % (
                self.model._meta.app_label,
                self.model._meta.object_name.lower(),
                self.json_template_name_suffix
            ))
        return names

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        response_kwargs['content_type'] = 'application/json'
        return self.response_class(
            request = self.request,
            template = self.get_json_template_names(),
            context = context,
            **response_kwargs
        )


#==============================================================================
# JSONMultipleObjectTemplateResponseMixin
#=============================================================================
class JSONMultipleObjectTemplateResponseMixin(TemplateResponseMixin):
    """
    A mixin that can be used to render a templated JSON response.
    """
    json_template_name_suffix = '_list'

    def get_json_template_names(self):
        """
        Return a list of template names to be used for the request. Must return
        a list. May not be called if get_template is overridden.
        """
        try:
            names = super(JSONMultipleObjectTemplateResponseMixin, self).get_json_template_names()
        except (ImproperlyConfigured, AttributeError):
            # 'super' object has no attribute 'get_json_template_names'
            # or
            # If template_name isn't specified, it's not a problem --
            # we just start with an empty list.
            names = []

        # If the list is a queryset, we'll invent a template name based on the
        # app and model name. This name gets put at the end of the template
        # name list so that user-supplied names override the automatically-
        # generated ones.
        if hasattr(self.object_list, 'model'):
            opts = self.object_list.model._meta
            names.append("%s/%s%s.json" % (opts.app_label, opts.object_name.lower(), self.json_template_name_suffix))
        return names

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        response_kwargs['content_type'] = 'application/json'
        return self.response_class(
            request = self.request,
            template = self.get_json_template_names(),
            context = context,
            **response_kwargs
        )


#==============================================================================
# JSMultipleObjectTemplateResponseMixin
#=============================================================================
class JSMultipleObjectTemplateResponseMixin(TemplateResponseMixin):
    """
    A mixin that can be used to render a templated JS response.
    """
    js_template_name_suffix = '_list'

    def get_js_template_names(self):
        """
        Return a list of template names to be used for the request. Must return
        a list. May not be called if render_to_response is overridden.
        """
        try:
            names = super(JSMultipleObjectTemplateResponseMixin, self).get_js_template_names()
        except (ImproperlyConfigured, AttributeError):
            # 'super' object has no attribute 'get_js_template_names'
            # or
            # If template_name isn't specified, it's not a problem --
            # we just start with an empty list.
            names = []

        # If the list is a queryset, we'll invent a template name based on the
        # app and model name. This name gets put at the end of the template
        # name list so that user-supplied names override the automatically-
        # generated ones.
        if hasattr(self.object_list, 'model'):
            opts = self.object_list.model._meta
            names.append("%s/%s%s.js" % (opts.app_label, opts.object_name.lower(), self.js_template_name_suffix))
        return names

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a JS response, transforming 'context' to make the payload.
        """
        response_kwargs['content_type'] = 'application/javascript'
        return self.response_class(
            request = self.request,
            template = self.get_js_template_names(),
            context = context,
            **response_kwargs
        )
