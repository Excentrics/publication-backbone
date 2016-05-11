# -*- coding: utf-8 -*-
import os

from random import randint
from django.utils.translation import ugettext_lazy as _
from django import template
from django.contrib.sites.models import Site

from classytags.helpers import InclusionTag
from classytags.core import Options, Tag
from classytags.arguments import MultiKeywordArgument, Argument

from publication_backbone import conf as config
from publication_backbone.models import BaseCategory, Category, StaticPlaceholder
from fluent_pages.models import UrlNode
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()


class Category_SEO(InclusionTag):
    """
    Inclusion tag for displaying categories.
    """
    template = 'publication_backbone/templatetags/category_seo/_category_seo.html'
    options = Options(
        MultiKeywordArgument('kwargs', required=False),
    )

    def get_context(self, context, kwargs):
        nodes = kwargs.get('nodes')
        if nodes is None:
            nodes = BaseCategory.objects.visible()
        context.update({
            'nodes': nodes,
            })
        return context

register.tag(Category_SEO)


class Render_PL(InclusionTag):
    """
    Inclusion tag for static placeholder.
    """
    template = 'publication_backbone/templatetags/_staticplaceholder.html'
    options = Options(
        Argument('placeholder', resolve=True),
        )

    def get_context(self, context, placeholder):

        placeholder_object = StaticPlaceholder.objects.get(slug=placeholder)
        context.update({
            'placeholder_object': placeholder_object,
        })
        return context

register.tag(Render_PL)


class Currency_sign(InclusionTag):
    """
    Inclusion tag for displaying Currency sign.
    """
    template = 'publication_backbone/templatetags/currency/_currency_sign.html'

    def get_context(self, context):
        language_code = context.get('LANGUAGE_CODE')
        return {
            'LANGUAGE_CODE': language_code
        }
register.tag(Currency_sign)


class Site_name(Tag):
    options = Options(
        'as',
        Argument('varname', required=False, resolve=False)
    )

    def render_tag(self, context, varname):
        output = Site.objects.get_current().name
        if varname:
            context[varname] = output
            return ''
        return output

register.tag(Site_name)


class Site_domain(Tag):
    options = Options(
        'as',
        Argument('varname', required=False, resolve=False)
    )

    def render_tag(self, context, varname):
        output = Site.objects.get_current().domain
        if varname:
            context[varname] = output
            return ''
        return output

register.tag(Site_domain)


class Promo_item_divider(Tag):
    options = Options(
        'as',
        Argument('varname', required=False, resolve=False)
    )

    def render_tag(self, context, varname):
        COLUMN_DIVIDERS = [6,5,4,3,2]
        ic = config.PUBLICATION_BACKBONE_PROMOTION_PER_PAGE_ITEMS_COUNT
        divider = None
        for cd in COLUMN_DIVIDERS:
            n = ic % cd
            if n == 0:
                if cd != 6:
                    divider = cd
                    break
                else:
                    if ic > 12:
                        divider = cd
                        break
        if varname:
            context[varname] = divider
            return ''
        return divider

register.tag(Promo_item_divider)


class Get_config(Tag):
    options = Options(
        'as',
        Argument('var_name', required=True, resolve=False)
    )

    def render_tag(self, context, var_name):
        context[var_name] = config
        return ''

register.tag(Get_config)


@register.filter
def filename(value):
    try:
        fn = os.path.basename(value.file.name)
    except:
        fn = None
    return fn


@register.filter
def check_marks_tag_on_key(marks, key):
    result = False
    if marks and key:
        for mark in marks:
            if key in mark.tags:
                result = True
    return result


class Category_sitemap(InclusionTag):
    """
    Inclusion tag for displaying categories.
    """
    template = 'publication_backbone/templatetags/category_seo/_category_sitemap.html'
    options = Options(
        MultiKeywordArgument('kwargs', required=False),
    )

    def get_context(self, context, kwargs):
        nodes = kwargs.get('nodes')
        if nodes is None:
            nodes = BaseCategory.objects.visible()
            cat_cnt = Category.objects.visible().count()
        else:
            cat_cnt = 0

        tmp = randint(1 - cat_cnt / 4, cat_cnt) if cat_cnt else 0

        excluded_page_nodes = []
        category_nodes = []
        for node in nodes:
            if node.get_real_instance_class_name() == 'CategoryLink':
                excluded_page_nodes.append(node.get_url())
            elif node.get_real_instance_class_name() != 'CategoryDivider':
                category_nodes.append(node.get_catalog_url())

        orphans_page_nodes = UrlNode.objects.filter(in_navigation=False, status='p')

        site_url = 'http://' + Site.objects.get_current().domain

        page_nodes = UrlNode.objects.filter(status='p')
        redirect_url_nodes = {}
        for node in page_nodes:
            if hasattr(node, 'new_url'):
                redirect_url = node.new_url.replace(site_url, '')
                if redirect_url in category_nodes:
                    excluded_page_nodes.append(node.url)
                elif redirect_url in excluded_page_nodes:
                    excluded_page_nodes.append(node.url)
                    redirect_url_nodes[redirect_url] = node.url

        context.update({
            'nodes': nodes,
            'category_rnd_index': tmp,
            'excluded_page_nodes': excluded_page_nodes,
            'orfans_page_nodes': orphans_page_nodes,
            'redirect_url_nodes': redirect_url_nodes,
        })
        return context

register.tag(Category_sitemap)
