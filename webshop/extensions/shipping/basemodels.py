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


class ShippedItemBase(AbstractPricedItemBase):
    """ Base class for shippable items. """

    def get_shipping_costs(self, **kwargs):
        """
        Return the most sensible shipping cost associated with this item.
        By default, it returns the total shipping cost as yielded by
        `get_total_shipping_costs`.
        """
        return self.get_total_shipping_costs(**kwargs)

    def get_total_shipping_costs(self, **kwargs):
        """
        Return the total shipping applicable for this item. Must be
        implemented in subclasses.
        """
        raise NotImplementedError

    def get_price_with_shipping(self, **kwargs):
        """ Get the price with shipping costs applied. """
        return self.get_price(**kwargs) + self.get_shipping_costs(**kwargs)


class ShippedCartBase(ShippedItemBase):
    """
    Mixin class for shopping carts with shipping costs associated with them.
    """

    def get_total_shipping_costs(self, **kwargs):
        """
        Get the total shipping cost for this `Cart`, summing up the shipping
        costs for the whole order and those for individual items (where
        applicable).
        """
        cost = self.get_order_shipping_costs(**kwargs)

        for item in self.get_items():
            cost += item.get_shipping_costs(**kwargs)

        assert cost < self.get_price(**kwargs), \
            'Shipping costs should not be higher than price of Cart.'

        return cost

    def get_order_shipping_costs(self, **kwargs):
        """
        Get the shipping costs for this order. Must be implemented in
        subclasses.
        """
        raise NotImplementedError


class ShippedCartItemBase(ShippedItemBase):
    """
    Mixin class for `CartItemz`'s with a function `get_shipping_costs()`.
    """

    def get_shipping_costs(self, **kwargs):
        """ Get the shipping costs for this `CartItem`. """
        raise NotImplementedError
