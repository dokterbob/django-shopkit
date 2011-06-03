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

def get_currency_field():
    """
    Use this method to get a useable pricefield based on the
    `SHOPKIT_PRICE_FIELD_NAME` setting::

        # Get the currently configured currency field, whatever it is
        from shopkit.extensions.currency.utils import get_currency_field
        PriceField = get_currency_field()

        class PricedModel(models.Model):
            ...
            price = PriceField()

"""
    from shopkit.extensions.currency.settings import PRICE_FIELD_NAME

    # If we're just documenting, return some bogus value here
    if PRICE_FIELD_NAME == '#doc':
        class Bogus(object):
            def __init__(self, *args, **kwargs):
                pass

        return Bogus

    module_name, field_name = PRICE_FIELD_NAME.rsplit('.', 1)

    # Allright, this is ugly as a monkey right here
    # Ref: http://stackoverflow.com/questions/2724260/why-does-pythons-import-require-fromlist
    module = __import__(module_name, fromlist=(field_name, ))
    price_field = getattr(module, field_name)

    return price_field

