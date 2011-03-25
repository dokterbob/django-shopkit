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

from decimal import Decimal

from django.db import models
from django.utils.translation import ugettext_lazy as _

# Get the currently configured currency field, whatever it is
from webshop.extensions.currency.utils import get_currency_field
PriceField = get_currency_field()

from webshop.core.basemodels import AbstractPricedItemBase

from webshop.extensions.shipping.settings import ADDRESS_MODEL


class ShippedItemBase(AbstractPricedItemBase):
    """ Base class for shippable items. """

    class Meta:
        abstract = True

    def get_shipping_costs(self, **kwargs):
        """
        Return the most sensible shipping cost associated with this item.
        By default, it returns the total shipping cost as yielded by
        `get_total_shipping_costs`.
        """
        shipping_costs = self.get_total_shipping_costs(**kwargs)

        logger.debug('Total shipping costs for %s: %s',
                     self, shipping_costs)

        return shipping_costs

    def get_total_shipping_costs(self, **kwargs):
        """
        Return the total shipping applicable for this item. Must be
        implemented in subclasses.
        """

        raise NotImplementedError

    def get_price_without_shipping(self, **kwargs):
        """ Get the price without shipping costs. """
        return super(ShippedItemBase, self).get_price(**kwargs)

    def get_price(self, **kwargs):
        """ Get the price with shipping costs applied. """
        without = self.get_price_without_shipping(**kwargs)
        shipping_costs = self.get_shipping_costs(**kwargs)

        return without + shipping_costs


class ShippedCartBase(ShippedItemBase):
    """
    Mixin class for shopping carts with shipping costs associated with them.
    """

    class Meta:
        abstract = True

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

    class Meta:
        abstract = True


class ShippedOrderBase(ShippedItemBase):
    """
    Mixin class for orders with shipping costs associated with them.
    """

    class Meta:
        abstract = True

    shipping_address = models.ForeignKey(ADDRESS_MODEL, null=True, blank=True,
                                        related_name='shippable%(class)s_set')
    """ Shipping address for this order"""

    order_shipping_costs = PriceField(default=Decimal('0.00'),
                                      verbose_name=_('order shipping costs'))
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
        costs = self.get_order_shipping_costs()

        for item in self.get_items():
            item_costs = item.get_shipping_costs()
            assert isinstance(item_costs, Decimal)
            costs += item_costs

        return costs

    def update_shipping(self):
        """ Update the shipping costs for order and order items. """

        # Make sure we call the superclass here
        superclass = super(ShippedOrderBase, self)
        
        self.order_shipping_costs = superclass.get_order_shipping_costs()

        logger.debug(u'Updating order shipping costs for %s to %s',
                     self, self.order_shipping_costs)

        for item in self.get_items():
            item.update_shipping()


class ShippedOrderItemBase(ShippedItemBase):
    """
    Mixin class for `OrderItem`'s with shipping costs associated with them.
    """

    class Meta:
        abstract = True

    shipping_costs = PriceField(default=Decimal('0.00'),
                                verbose_name=_('shipping cost'))
    """ Shipping costs for this item. """

    def get_shipping_costs(self, **kwargs):
        """ Return the shipping costs for this item. """
        return self.shipping_costs

    def update_shipping(self):
        """ Update shipping costs - does *not* save the object. """

        # Make sure we call the superclass here
        superclass = super(ShippedOrderItemBase, self)

        self.shipping_costs = superclass.get_shipping_costs()

        logger.debug(u'Updating order shipping costs for %s to %s',
                     self, self.shipping_costs)
