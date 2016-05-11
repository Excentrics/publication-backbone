# -*- coding: utf-8 -*-
import django
from django import template

from classytags.core import Options, Tag
from classytags.arguments import MultiValueArgument, Argument

from django.core.cache import cache


register = template.Library()


if django.VERSION >= (1, 6):
    from django.core.cache.utils import make_template_fragment_key
else:
    import hashlib
    from django.utils.encoding import force_bytes
    from django.utils.http import urlquote

    TEMPLATE_FRAGMENT_KEY_TEMPLATE = 'template.cache.%s.%s'

    def make_template_fragment_key(fragment_name, vary_on=None):
        if vary_on is None:
            vary_on = ()
        key = ':'.join(urlquote(var) for var in vary_on)
        args = hashlib.md5(force_bytes(key))
        return TEMPLATE_FRAGMENT_KEY_TEMPLATE % (fragment_name, args.hexdigest())


class Get_cache(Tag):

    options = Options(
        Argument('fragment_name', resolve=True),
        MultiValueArgument('vary_on', required=False),
        'as',
        Argument('var_name', required=False, resolve=False)
    )

    def render_tag(self, context, fragment_name, vary_on, var_name):
        key = make_template_fragment_key(fragment_name, vary_on)
        result = cache.get(key)
        if var_name:
            context[var_name] = result
            return ''
        return result

register.tag(Get_cache)


class Delete_cache(Tag):

    options = Options(
        Argument('fragment_name', resolve=True),
        MultiValueArgument('vary_on', required=False)
    )

    def render_tag(self, context, fragment_name, vary_on):
        key = make_template_fragment_key(fragment_name, vary_on)
        cache.delete(key)
        return ''

register.tag(Delete_cache)