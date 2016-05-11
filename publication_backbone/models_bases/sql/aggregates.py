# -*- coding: utf-8 -*-
"""
Classes to represent the custom SQL aggregate functions
"""
from django.db.models.sql.aggregates import Aggregate


class Dummy(Aggregate):
    sql_function = None
    sql_template = '%(field)s'

    def __init__(self, col, **extra):
        super(Dummy, self).__init__(col, **extra)
