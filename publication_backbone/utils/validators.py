# -*- coding: utf-8 -*-
from django.core import validators


class URLOrAbsolutePathValidator(validators.URLValidator):
    @staticmethod
    def is_absolute_path(value):
        return value.startswith('/')

    def __call__(self, value):
        if URLOrAbsolutePathValidator.is_absolute_path(value):
            return None
        else:
            return super(URLOrAbsolutePathValidator, self).__call__(value)