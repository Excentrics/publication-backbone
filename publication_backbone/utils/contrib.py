#-*- coding: utf-8 -*-
import os
import hashlib
import struct
from binascii import hexlify
from pytils.translit import slugify

from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _
import re


#==============================================================================
# create_hash
#==============================================================================
def create_hash(key):
    hash = hashlib.md5()
    hash.update(key)
    return hash.hexdigest()


#==============================================================================
# hash_unsorted_list
#==============================================================================
def hash_unsorted_list(value):
    lst = list(value)
    lst.sort()
    return create_hash('.'.join([str(x) for x in lst]))


#==============================================================================
# create_uid
#==============================================================================
def create_uid():
    return hexlify(os.urandom(16))


#==============================================================================
# get_unique_slug
#==============================================================================
def get_unique_slug(name, key=None):
    slugify_name = ''.join([slugify(u'%s' % name)[:18], create_uid() if key is None else create_hash(str(key))])
    return slugify_name


#==============================================================================
# uniq
#==============================================================================
def uniq(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if x not in seen and not seen_add(x)]


#==============================================================================
# float_to_bits
#==============================================================================
'''
def float_to_bits(f):
    s = struct.pack('>f', f)
    return struct.unpack('>l', s)[0]
'''

#==============================================================================
# bits_to_float
#==============================================================================
def bits_to_float(b):
    s = struct.pack('>l', b)
    return struct.unpack('>f', s)[0]


def get_object(path, fail_silently=False):
    # Return early if path isn't a string (might already be an callable or
    # a class or whatever)
    if not isinstance(path, (str, unicode)):
        return path
    try:
        return import_module(path)
    except ImportError:
        try:
            dot = path.rindex('.')
            mod, fn = path[:dot], path[dot + 1:]
            return getattr(import_module(mod), fn)
        except (AttributeError, ImportError):
            if not fail_silently:
                raise


def get_dict_from_address_text(keypare_text):
    keypare_dict = {}
    if keypare_text:
        for line in keypare_text.split('\n'):
            keypare = line.split(':')
            if len(keypare) > 1 and keypare[0] <> '':
                key = keypare[0].lstrip()
                value = re.sub('\r', '', keypare[1].lstrip())
                keypare_dict[key] = re.sub(',$', '', value)
    return keypare_dict


def get_name_from_address_text(address_text, key):
    keypare_dict = get_dict_from_address_text(address_text)
    if len(keypare_dict) >= 1:
        result = keypare_dict.get(key, _('Error import customer name from address!'))
    else:
        result = ''
    return result


