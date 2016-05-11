# -*- coding: utf-8 -*-
from django import template
from django.core.paginator import EmptyPage

from classytags.core import Options, Tag
from classytags.arguments import MultiKeywordArgument, Argument
from classytags.helpers import InclusionTag

from publication_backbone.utils.paginator import Paginator, OffsetNotAnInteger


register = template.Library()


class Paginate(Tag):
    """Paginate objects.
    Usage:
    .. code-block:: html+django
        {% paginate entries as page_entries %}
    """

    options = Options(
        Argument('object_list', resolve=True),
        MultiKeywordArgument('kwargs', required=False),
        'as',
        Argument('var_name', resolve=False)
    )

    paginator_class = Paginator

    def render_tag(self, context, object_list, kwargs, var_name):
        object_list_key = var_name
        paginator_key = "%s_paginator" % var_name
        page_obj_key = "%s_page_obj" % var_name
        is_paginated_key = "%s_is_paginated" % var_name
        per_page = kwargs.get('per_page')
        per_page = None if per_page is None else int(per_page)
        if per_page:
            orphans = kwargs.get('orphans')
            orphans = 0 if orphans is None else int(orphans)
            offset = kwargs.get('offset', 0)
            paginator = self.get_paginator(object_list, per_page, orphans)
            try:
                page = paginator.page_by_offset(offset)
            except OffsetNotAnInteger:
                # If page is not an integer, deliver first page.
                page = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                page = paginator.page(paginator.num_pages)
            extra_context = {
                paginator_key: paginator,
                page_obj_key: page,
                is_paginated_key: page.has_other_pages(),
                object_list_key: page.object_list
            }
        else:
            extra_context = {
                paginator_key: None,
                page_obj_key: None,
                is_paginated_key: False,
                object_list_key: object_list
            }
        context.update(extra_context)
        return ''

    def get_paginator(self, object_list, per_page, orphans):
        return self.paginator_class(object_list, per_page, orphans)

register.tag(Paginate)


class Paginator(InclusionTag):
    template = 'publication_backbone/templatetags/pagination/paginator.html'
    options = Options(
        MultiKeywordArgument('kwargs', required=False),
    )

    def get_context(self, context, kwargs):
        page_obj = kwargs.get('page_obj', context.get('page_obj', None))
        result = {
            'page_obj': page_obj,
        }
        if not page_obj is None:
            url_root = kwargs.get('url_root', '')
            adjacent_pages = kwargs.get('adjacent_pages', 2)
            current_page = page_obj.number
            num_pages = page_obj.paginator.num_pages
            start_page = max(current_page - adjacent_pages, 1)
            if start_page <= 3:
                start_page = 1
            end_page = current_page + adjacent_pages + 1
            if end_page >= num_pages - 1:
                end_page = num_pages + 1
            page_numbers = [n for n in range(start_page, end_page)]
            result.update({
                'url_root': url_root,
                'num_pages': num_pages,
                'page_numbers': page_numbers,
                'show_first': 1 not in page_numbers,
                'show_last': num_pages not in page_numbers,
                'current_page': current_page,
            })
        return result

register.tag(Paginator)