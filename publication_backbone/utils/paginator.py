# -*- coding: utf-8 -*-
__author__ = 'LEGION'

from django.core import paginator

class OffsetNotAnInteger(paginator.InvalidPage):
    pass

class Paginator(paginator.Paginator):

    def validate_offset(self, offset):
        "Validates the given offset."
        try:
            offset = int(offset)
        except (TypeError, ValueError):
            raise OffsetNotAnInteger('That offset is not an integer')
        return offset

    def page_by_offset(self, offset):
        "Returns a Page object for the given offset."
        number = self.validate_number(self.validate_offset(offset) // self.per_page + 1)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count
        return Page(self.object_list[bottom:top], number, self)

    def page(self, number):
        "Returns a Page object for the given 1-based page number."
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count
        return Page(self.object_list[bottom:top], number, self)


class Page(paginator.Page):

    def offset(self):
        """
        Returns the offset
        """
        # Special case, return zero if no items.
        if self.paginator.count == 0:
            return 0
        return self.paginator.per_page * (self.number - 1)

    def limit(self):
        return self.paginator.per_page

    def next_offset(self):
        return self.paginator.per_page * self.number

    def previous_offset(self):
        return self.paginator.per_page * (self.number - 2)
