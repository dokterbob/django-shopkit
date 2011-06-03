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

from decimal import Decimal
from django.db.models.fields import DecimalField


class MinMaxDecimalField(DecimalField):
    """
    `DecimalField` subclass which allows specifying a minimum and maximum
    value. Takes two extra optional parameters, to be specified as a Decimal
    or string:

    * `max_value`
    * `min_value`
    """

    description = 'DecimalField subclass which allows specifying a minimum \
                   and maximum value.'

    def __init__(self, **kwargs):
        self.max_value = kwargs.pop('max_value', None)
        self.min_value = kwargs.pop('min_value', None)

        super(MinMaxDecimalField, self).__init__(**kwargs)


    def formfield(self, **kwargs):
        if not self.max_value is None:
            kwargs['max_value'] = Decimal(self.max_value)

        if not self.min_value is None:
            kwargs['min_value'] = Decimal(self.min_value)

        return super(MinMaxDecimalField, self).formfield(**kwargs)


class PercentageField(MinMaxDecimalField):
    """
    Subclass of `DecimalField` with sensible defaults for percentage
    discounts:

    * `max_value=100`
    * `min_value=0`
    * `decimal_places=0`
    * `max_digits=3`

    """


    description = 'Subclass of DecimalField with sensible defaults for \
                   percentage discounts.'

    def __init__(self, **kwargs):
        kwargs['max_value'] = kwargs.get('max_value', Decimal('100'))
        kwargs['min_value'] = kwargs.get('min_value', Decimal('0'))
        kwargs['decimal_places'] = kwargs.get('decimal_places', 0)
        kwargs['max_digits'] = kwargs.get('max_digits', 3)

        super(PercentageField, self).__init__(**kwargs)
