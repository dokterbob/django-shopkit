# Copyright (C) 2010-2011 Mathijs de Bruin <mathijs@mathijsfietst.nl>
#
# This file is part of django-webshop.
#
# django-webshop is free software; you can redistribute it and/or modify
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

from webshop.core.basemodels import AbstractPricedItemBase


class DiscountedItemBase(AbstractPricedItemBase):
    """ Mixin class for discounted items. """

    class Meta:
        abstract = True

    def get_discount(self, **kwargs):
        """
        Return the most sensible discount related to this item. By default,
        it returns the total discount applicable as yielded by
        `get_total_discount`.
        """

        return self.get_total_discount(**kwargs)

    def get_total_discount(self, **kwargs):
        """
        Return the total discount applicable for this item. Must be
        implemented in subclasses.
        """

        raise NotImplementedError

    def get_price_with_discount(self, **kwargs):
        """ Get the price with the discount applied. """
        assert self.get_total_discount(**kwargs) < self.get_price(**kwargs), \
            'Discount is higher than item price - discounted price would be\
             negative!'

        return self.get_price(**kwargs) - self.get_total_discount(**kwargs)



""" 
.. todo::
    It is not clear whether the latter two models have any function at all
    Consider deleting them.
"""
class DiscountedCartBase(DiscountedItemBase):
    """
    Base class for shopping carts which can have discounts applied to them.
    """

    class Meta:
        abstract = True

    def get_total_discount(self, **kwargs):
        """
        Return the total discount. This consists of the sum of discounts
        applicable to orders and the discounts applicable to items.
        """
        discount = self.get_order_discount(**kwargs)

        for item in self.get_items():
            discount += item.get_discount(**kwargs)

        # Make sure the discount is never higher than the price of 
        # the oringal item
        price = self.get_price(**kwargs)
        if discount > price:
            return price

        return discount

    def get_order_discount(self, **kwargs):
        """
        Calculate the whole order discount, as distinct from discount
        that apply to specific order items. This method must be implemented
        in subclasses.
        """
        raise NotImplementedError


class DiscountedCartItemBase(DiscountedItemBase):
    """
    Base class for shopping cart items which can have discounts applied to
    them.
    """

    class Meta:
        abstract = True

    def get_discount(self, **kwargs):
        """
        Get the discount applicable to this item. This method must be
        implemented in subclasses.
        """
        raise NotImplementedError

