"""
Classes to represent the definitions of aggregate functions.
"""

from django.db.models import aggregates
from publication_backbone.models_bases.sql import aggregates as aggregates_module


class Aggregate(aggregates.Aggregate):

    def add_to_query(self, query, alias, col, source, is_summary):
        """Add the aggregate to the nominated query.

        This method is used to convert the generic Aggregate definition into a
        backend-specific definition.

         * query is the backend-specific query instance to which the aggregate
           is to be added.
         * col is a column reference describing the subject field
           of the aggregate. It can be an alias, or a tuple describing
           a table and column name.
         * source is the underlying field or aggregate definition for
           the column reference. If the aggregate is not an ordinal or
           computed type, this reference is used to determine the coerced
           output type of the aggregate.
         * is_summary is a boolean that is set True if the aggregate is a
           summary value rather than an annotation.
        """
        klass = getattr(aggregates_module, self.name)
        aggregate = klass(col, source=source, is_summary=is_summary, **self.extra)
        query.aggregates[alias] = aggregate


class Dummy(Aggregate):
    name = 'Dummy'