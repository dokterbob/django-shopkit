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

        ..todo::
            The mechanism making sure the discount is never higher than the
            original price is implemented here as well as in get_total_discount
            of DiscountedCartBase and DiscountedOrderBase.
        """

        discount = self.get_total_discount(**kwargs)

        return discount

    def get_piece_discount(self, **kwargs):
        """
        Get the discount per piece. Must be implemented in subclasses.
        """
        raise NotImplementedError

    def get_total_discount(self, **kwargs):
        """
        Return the total discount applicable for this item. Must be
        implemented in subclasses.
        """
        raise NotImplementedError

    def get_price_without_discount(self, **kwargs):
        """
        The price without discount. Wrapper around the `get_price`
        method of the superclass.
        """
        return super(DiscountedItemBase, self).get_price(**kwargs)

    def get_piece_price_without_discount(self, **kwargs):
        """
        The price per piece without discount. Wrapper around the
        `get_piece_price` method of the superclass.
        """
        return super(DiscountedItemBase, self).get_piece_price(**kwargs)

    def get_piece_price_with_discount(self, **kwargs):
        """ Get the piece price with the discount applied. """
        undiscounted = self.get_piece_price_without_discount(**kwargs)
        discount = self.get_piece_discount(**kwargs)

        assert discount <= undiscounted, \
            'Discount is higher than item price - discounted price negative!'

        return undiscounted - discount

    def get_price(self, **kwargs):
        """ Get the price with the discount applied. """
        undiscounted = self.get_price_without_discount(**kwargs)
        discount = self.get_discount(**kwargs)

        assert discount <= undiscounted, \
            'Discount is higher than item price - discounted price negative!'

        return undiscounted - discount


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
            item_discount = item.get_discount(**kwargs)
            assert isinstance(item_discount, Decimal)
            assert item_discount <= item.get_price_without_discount(), \
                'Discount is higher than item price - discounted price negative!'
            discount += item_discount

        # Make sure the discount is never higher than the price of
        # the oringal item
        price = self.get_price_without_discount(**kwargs)
        if discount > price:
            logger.info(u'Discount %s higher than price %s. Lowering to price.',
                       discount, price)
            discount = price

        return discount

    def get_order_discount(self, **kwargs):
        """
        Calculate the whole order discount, as distinct from discount
        that apply to specific order items. This method must be implemented
        elsewhere.
        """
        raise NotImplementedError


class DiscountedCartItemBase(DiscountedItemBase):
    """
    Base class for shopping cart items which can have discounts applied to
    them.
    """

    class Meta:
        abstract = True

    def get_total_discount(self, **kwargs):
        """
        Return the total discount for the CartItem, which is simply a wrapper
        around `get_item_discount`.
        """
        discount = self.get_item_discount(**kwargs)

        # Make sure the discount is never higher than the price of
        # the oringal item
        price = self.get_price_without_discount(**kwargs)
        if discount > price:
            logger.info(u'Discount %s higher than price %s. Lowering to price.',
                       discount, price)
            return price

        return discount


    def get_item_discount(self, **kwargs):
        """
        Calculate the order item discount, as distinct from the whole order
        discount. This method must be implemented in elsewhere.
        """
        raise NotImplementedError


class DiscountedOrderBase(DiscountedItemBase):
    """
    Base class for orders which can have discounts applied to them. This
    stores rather than calculates the discounts for order persistence.
    """

    class Meta:
        abstract = True

    order_discount = PriceField(verbose_name=_('order discount'),
                                default=Decimal('0.00'))
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
            item_discount = item.get_discount(**kwargs)
            assert isinstance(item_discount, Decimal)
            discount += item_discount

        # Make sure the discount is never higher than the price of
        # the oringal item
        price = self.get_price_without_discount(**kwargs)
        if discount > price:
            logger.info(u'Discount %s higher than price %s. Lowering to price.',
                       discount, price)
            return price

        return discount

    def get_order_discount(self):
        """
        Return the discount for this order. This basically returns the
        `order_discount` property. To recalculate/update this value, call the
        `update_discount` method.
        """
        return self.order_discount

    def update_discount(self):
        """ Update discounts for order and order items """

        # Make sure we call the superclass here
        superclass = super(DiscountedOrderBase, self)

        self.order_discount = superclass.get_order_discount()

        logger.debug(u'Updating order discount for %s to %s',
                     self, self.order_discount)

        for item in self.get_items():
            item.update_discount()


class DiscountedOrderItemBase(DiscountedItemBase):
    """
    Base class for order items which can have discounts applied to them.
    """
    class Meta:
        abstract = True

    discount = PriceField(verbose_name=_('discount'),
                          default=Decimal('0.00'))
    """ The amount of discount applied to this item. """

    def get_total_discount(self, **kwargs):
        """
        Return the total discount for the CartItem, which is simply a wrapper
        around `get_item_discount`.
        """
        return self.get_item_discount(**kwargs)

    def get_item_discount(self, **kwargs):
        """
        Return the discount for this item. This basically returns the
        `discount` property. To recalculate/update this value, call the
        `update_discount` method.
        """
        return self.discount

    def update_discount(self):
        """ Update the discount """

        # Make sure we call the superclass here
        superclass = super(DiscountedOrderItemBase, self)
        self.discount = superclass.get_discount()

        logger.debug(u'Updating item discount for %s to %s',
                     self, self.discount)

