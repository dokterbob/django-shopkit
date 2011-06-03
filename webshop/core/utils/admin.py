# Copyright (C) 2010-2011 Mathijs de Bruin <mathijs@mathijsfietst.nl>
#
# This file is part of django-shopkit.
#
# django-shopkit is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import logging

logger = logging.getLogger(__name__)


""" Generic Admin utilities """

class LimitedAdminInlineMixin(object):
    """
    InlineAdmin mixin limiting the selection of related items according to
    criteria which can depend on the current parent object being edited.

    A typical use case would be selecting a subset of related items from
    other inlines, ie. images, to have some relation to other inlines.

    Use as follows::

        class MyInline(LimitedAdminInlineMixin, admin.TabularInline):
            def get_filters(self, obj):
                return (('<field_name>', dict(<filters>)),)

    """

    @staticmethod
    def limit_inline_choices(formset, field, empty=False, **filters):
        """
        This function fetches the queryset with available choices for a given
        `field` and filters it based on the criteria specified in filters,
        unless `empty=True`. In this case, no choices will be made available.
        """
        assert formset.form.base_fields.has_key(field)

        qs = formset.form.base_fields[field].queryset
        if empty:
            logger.debug(u'Limiting the queryset to none')
            formset.form.base_fields[field].queryset = qs.none()
        else:
            qs = qs.filter(**filters)
            logger.debug(u'Limiting queryset for formset to: %s', qs)

            formset.form.base_fields[field].queryset = qs

    def get_formset(self, request, obj=None, **kwargs):
        """
        Make sure we can only select variations that relate to the current
        item.
        """
        formset = \
            super(LimitedAdminInlineMixin, self).get_formset(request,
                                                             obj,
                                                             **kwargs)

        for (field, filters) in self.get_filters(obj):
            if obj:
                self.limit_inline_choices(formset, field, **filters)
            else:
                self.limit_inline_choices(formset, field, empty=True)

        return formset

    def get_filters(self, obj):
        """
        Return filters for the specified fields. Filters should be in the
        following format::

            (('field_name', {'categories': obj}), ...)

        For this to work, we should either override `get_filters` in a
        subclass or define a `filters` property with the same syntax as this
        one.
        """
        return getattr(self, 'filters', ())
