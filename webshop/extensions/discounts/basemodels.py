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

from django.utils.translation import ugettext_lazy as _

# Get the currently configured currency field, whatever it is
from webshop.extensions.currency.utils import get_currency_field
PriceField = get_currency_field()


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


class DiscountedOrderBase(DiscountedItemBase):
    """
    Base class for orders which can have discounts applied to them. This
    stores rather thab calculates the discounts for order persistence.
    """

    class Meta:
        abstract = True

    order_discount = PriceField(verbose_name=_('order discount'))
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
        Create an order from the shopping cart, calculating possible
        discounts. Instantiates an order but does no saving.
        """
        order = super(DiscountedOrderBase, cls).from_cart(cart)

        order.update_discount()

        return order

    def get_order_discount(self):
        """
        Return the discount for this order. This basically returns the
        `order_discount` property. To recalculate/update this value, call the
        `update_discount` method.
        """
        return self.order_discount

    def update_discount(self, items=False):
        """
        Update order discounts - does *not* save the object. If items is
        specified, discounts for related `OrderItem`'s are updated as well.
        """
        # Make sure we call the superclass here
        superclass = super(DiscountedOrderBase, self)
        self.order_discount = superclass.get_order_discount()

        if items:
            for item in self.get_items():
                item.update_discount()


class DiscountedOrderItemBase(DiscountedItemBase):
    """
    Base class for order items which can have discounts applied to them.
    """
    class Meta:
        abstract = True

    discount = PriceField(verbose_name=_('discount'))
    """ The amount of discount applied to this item. """

    @classmethod
    def from_cartitem(cls, cartitem):
        """
        Create a discounted `OrderItem` from a `CartItem`, storing the
        discount amount in the `OrderItem`'s `discount` property.
        """
        superclass = super(DiscountedOrderItemBase, cls)
        orderitem = superclass.from_itemcart(cartitem)

        orderitem.update_discount()

        return orderitem

    def get_discount(self, **kwargs):
        """
        Return the discount for this item. This basically returns the
        `discount` property. To recalculate/update this value, call the
        `update_discount` method.
        """
        return self.discount

    def update_discount(self):
        """ Update the discount - does *not* save the object. """

        # Make sure we call the superclass here
        superclass = super(DiscountedOrderItemBase, self)
        self.discount = superclass.get_discount()

