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

from django.db import models
from django.utils.translation import ugettext_lazy as _

# Get the currently configured currency field, whatever it is
from webshop.extensions.currency.utils import get_currency_field
PriceField = get_currency_field()

from webshop.extensions.shipping.settings import ADDRESS_MODEL
from webshop.extensions.shipping.basemodels import ShippedItemBase


class ShippedOrderMixin(ShippedItemBase, models.Model):
    """
    Mixin class for orders with shipping costs associated with them.
    """

    class Meta:
        abstract = True

    shipping_address = models.ForeignKey(ADDRESS_MODEL,
                                        related_name='shippable%(class)s_set')
    """ Shipping address for this order"""

    order_shipping_costs = PriceField(_('whole order shipping cost'))
    """
    Shipping costs relating to the whole order and not individual items.
    """

    def get_order_shipping_costs(self, **kwargs):
        """
        Get the shipping costs for this order.
        """
        return self.order_shipping_costs

    def get_total_shipping_costs(self, **kwargs):
        """
        Get the total shipping cost for this `Cart`, summing up the shipping
        costs for the whole order and those for individual items (where
        applicable).
        """
        cost = self.get_order_shipping_costs()

        for item in self.get_items():
            cost += item.get_shipping_costs()

        return cost

    @classmethod
    def from_cart(cls, cart):
        """
        Create an order from the shopping cart, accounting for possible
        shipping costs. Instantiates an order but does no saving.
        """
        order = super(ShippedOrderMixin, cls).from_cart(cart)

        order.order_shipping_costs = cart.get_order_shipping_costs()

        return order


class ShippedOrderItemMixin(ShippedItemBase, models.Model):
    """
    Mixin class for `OrderItem`'s with shipping costs associated with them.
    """

    class Meta:
        abstract = True

    shipping_costs = PriceField(_('shipping cost'))
    """ Shipping costs for this item. """

    def get_shipping_costs(self, **kwargs):
        """ Return the shipping costs for this item. """
        return self.shipping_costs

    @classmethod
    def from_cartitem(cls, cartitem):
        """
        Create a discounted `OrderItem` from a `CartItem`, storing the
        shipping costs in the `OrderItem`'s `shipping_costs` property.
        """
        orderitem = super(ShippedOrderItemMixin, cls).from_cartitem(cartitem)

        orderitem.shipping_costs = cartitem.get_shipping_costs()

        return orderitem


class ShippableCustomerMixin(object):
    """
    Customer Mixin class for shops in which orders make use
    of a shipping address.
    """

    def get_recent_shipping(self):
        """ Return the most recent shipping address """
        latest_order = self.get_latest_order()

        return latest_order.shipping_address
