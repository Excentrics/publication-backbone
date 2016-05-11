#-*- coding: utf-8 -*-
from django import forms
from django.template.loader import render_to_string
from publication_backbone.models import (
    Rubric,
)
from publication_backbone.models_bases.rubricator import RubricInfo


class RubricTreeWidget(forms.SelectMultiple):
    def __init__(self, attrs=None):
        super(RubricTreeWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        if value:
            expanded_rubrics = list(set(RubricInfo.decompress(Rubric, value, fix_it=False).keys()).difference(set(value)))
        else:
            expanded_rubrics = list()
        return render_to_string(
                                 'admin/widgets/rubric_tree.html',
                                 { 'queryset': self.choices.queryset.all(),
                                   'name': name,
                                   'value': value,
                                   'attrs': attrs,
                                   'expanded_rubrics': expanded_rubrics,
                                   'is_characteristic': Rubric.ATTRIBUTE_IS_CHARACTERISTIC,
                                   'is_mark': Rubric.ATTRIBUTE_IS_MARK,
                                   'is_relation': Rubric.ATTRIBUTE_IS_RELATION
                                 }
                                )

    class Media:
        css = {
            'all': (
                '/static/publication_backbone/lib/font-awesome/css/font-awesome.min.css',
                '/static/admin/css/jquery.treeview.css',
            )
        }
        js = (
            '/static/admin/js/jquery.treeview.js',
            '/static/admin/js/treeview_init.js',
        )
