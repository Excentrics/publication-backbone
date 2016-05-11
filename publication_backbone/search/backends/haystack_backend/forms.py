# -*- coding: utf-8 -*-
from django import forms
from haystack.forms import HighlightedSearchForm
from django.utils.translation import ugettext_lazy as _


ORDER_CHOICES = (
        ('-_score', _('Order by Relevance')),
        ('-date_added', _('Order by Date')),
        #('-author', _('Order by Author')),
        #('-title', _('Order by Title')),
        #('-sub_name', _('Order by Subname')),
)


class PublicationSearchForm(HighlightedSearchForm):
    order = forms.ChoiceField(label=_('Sort order'),
                              required=False,
                              choices=ORDER_CHOICES,
                              initial=ORDER_CHOICES[0][0],
                              widget = forms.Select())

    def __init__(self, *args, **kwargs):
        super(PublicationSearchForm, self).__init__(*args, **kwargs)
        self.fields['q'].widget = forms.TextInput(attrs={'class': 'form-control'})

    def search(self):
        sqs = super(PublicationSearchForm, self).search()
        if not self.is_valid():
            return self.no_query_found()
        order_by = self.cleaned_data['order']

        if order_by:
            sqs = sqs.order_by(order_by)
        else:
            sqs = sqs.order_by(ORDER_CHOICES[0][0])

        return sqs