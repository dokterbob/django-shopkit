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

from webshop.extensions.discounts.basemodels import DiscountedItemBase


class DiscountedOrderMixin(DiscountedItemBase, models.Model):
    """
    Base class for orders which can have discounts applied to them. This
    stores rather thab calculates the discounts for order persistence.
    """

    class Meta:
        abstract = True

    order_discount = PriceField(verbose_name=_('whole order discount'))
    """
    Whole order discount, as distinct from discount
    that apply to specific order items.
    """

    def get_total_discount(self, **kwargs):
        """
        Return the total discount. This consists of the sum of discounts
        applicable to orders and the discounts applicable to items.
        """
        discount = self.order_discount

        for item in self.get_items():
            discount += item.get_discount(**kwargs)

        # Make sure the discount is never higher than the price of
        # the oringal item
        price = self.get_price(**kwargs)
        if discount > price:
            return price

        return discount

    @classmethod
    def from_cart(cls, cart):
        """
        Create an order from the shopping cart, accounting for possible
        order discounts. Instantiates an order but does no saving.
        """
        order = super(DiscountedOrderMixin, cls).from_cart(cart)

        order.order_discount = cart.get_order_discount()

        return order


class DiscountedOrderItemMixin(DiscountedItemBase, models.Model):
    """
    Mixin class for order items which can have discounts applied to them.
    """
    class Meta:
        abstract = True

    discount = PriceField(verbose_name=_('discount'))
    """ The amount of discount applied to this item. """

    def get_discount(self, **kwargs):
        """
        Wrapper around the `discount` property, providing for a generic API.
        """
        return self.discount

    @classmethod
    def from_cartitem(cls, cartitem):
        """
        Create a discounted `OrderItem` from a `CartItem`, storing the
        discount amount in the `OrderItem`'s `discount` property.
        """
        superclass = super(DiscountedOrderItemMixin, cls)
        orderitem = superclass.from_itemcart(cartitem)

        orderitem.discount = cartitem.get_discount()

        return orderitem
