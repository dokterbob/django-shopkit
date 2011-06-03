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

# Inspired by django-shop:
# https://github.com/divio/django-shop/blob/master/shop/util/fields.py

from django.db.models.fields import DecimalField

from webshop.extensions.currency.simple.settings import CURRENCY_MAX_DIGITS, \
                                                        CURRENCY_DECIMALS


class PriceField(DecimalField):
    """
    A PriceField is simply a subclass of DecimalField with common defaults
    set by `CURRENCY_MAX_DIGITS` and `CURRENCY_DECIMALS`.
    """
    def __init__(self, **kwargs):
        kwargs['max_digits'] = \
            kwargs.get('max_digits', CURRENCY_MAX_DIGITS)

        kwargs['decimal_places'] = \
            kwargs.get('decimal_places', CURRENCY_DECIMALS)

        return super(PriceField, self).__init__(**kwargs)