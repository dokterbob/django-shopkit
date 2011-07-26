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

"""
Model base and mixin classes for carts and orders with calculated
discounts.

.. todo::
    Provide a listing/overview of the types of DiscountMixin's available,
    how they should be used and... whether they have been tested or not.

"""

import logging
logger = logging.getLogger(__name__)

from django.db import models
from django.utils.translation import ugettext_lazy as _

from decimal import Decimal

from webshop.extensions.discounts.settings import COUPON_LENGTH

from webshop.extensions.discounts.basemodels import \
    DiscountedCartBase, DiscountedCartItemBase, \
    DiscountedOrderBase, DiscountedOrderItemBase

from webshop.extensions.discounts.settings import DISCOUNT_MODEL
from webshop.core.utils import get_model_from_string


class CalculatedDiscountMixin(object):
    """
    Base class for items for which the discount is calculated using
    a `Discount` model.
    """

    def get_valid_discounts(self, **kwargs):
        """ Return valid discounts for the given arguments. """

        discount_class = get_model_from_string(DISCOUNT_MODEL)
        return discount_class.get_valid_discounts(**kwargs)


class CalculatedOrderDiscountMixin(CalculatedDiscountMixin):
    """
    Mixin class for discounted objects for which an order discount can be
    calculated by calling `get_order_discount` and valid discounts can be
    obtained by calling `get_valid_discounts`.
    """
    def get_valid_discounts(self, **kwargs):
        """ Return valid discounts for the current order. """
        superclass = super(CalculatedOrderDiscountMixin, self)

        discounts = \
            superclass.get_valid_discounts(order_discounts=True, **kwargs)

        logger.debug(u'Returning %s as valid order discounts for %s',
                     discounts, self)

        return discounts

    def get_order_discount(self, **kwargs):
        """
        Get the discount specific for this `Order`.
        """

        # Now, add discounts on the total order
        valid_discounts = self.get_valid_discounts(**kwargs)
        price = self.get_price_without_discount(**kwargs)

        total_discount = Decimal('0.00')
        for discount in valid_discounts:
            total_discount += discount.get_discount(order_price=price,
                                                    **kwargs)

        return total_discount


class CalculatedItemDiscountMixin(CalculatedDiscountMixin):
    """
    Mixin class for discounted objects for which an item discount can be
    calculated by calling `get_order_discount` and valid discounts can be
    obtained by calling `get_valid_discounts`.
    """

    def get_valid_discounts(self, **kwargs):
        """ Return valid discounts for the current order. """
        superclass = super(CalculatedItemDiscountMixin, self)

        assert not 'product' in kwargs

        discounts = \
            superclass.get_valid_discounts(product=self.product,
                                           item_discounts=True,
                                           **kwargs)

        logger.debug(u'Returning %s as valid order item discounts for %s',
                     discounts, self)

        return discounts


    def get_item_discount(self, **kwargs):
        """
        Get the total discount for this OrderItem.
        """

        valid_discounts = self.get_valid_discounts(**kwargs)
        price = self.get_price_without_discount(**kwargs)

        total_discount = Decimal('0.00')
        for discount in valid_discounts:
            item_discount = discount.get_discount(item_price=price, \
                                                  **kwargs)
            total_discount += item_discount * self.quantity

        return total_discount


class PersistentDiscountedItemBase(models.Model):
    """
    Mixin class for `Order`'s and `OrderItem`'s for which calculated discounts
    are persistently stored in a `discounts` property upon calling the
    `update_discount` method.
    """
    class Meta:
        abstract = True

    discounts = models.ManyToManyField(DISCOUNT_MODEL)

    def update_discount(self):
        """
        Call `update_discount` on the superclass to calculate the amount of
        discount, then store valid `Discount` objects for this order item.
        """
        super(PersistentDiscountedItemBase, self).update_discount()

        assert self.pk, 'Object not saved, need PK for assigning discounts'
        discounts = self.get_valid_discounts()

        # This assertion is not valid anymore for order item discounts
        # assert self.get_discount() == Decimal('0.00') or \
        #     (self.get_discount() and discounts)

        logger.debug(u'Storing discounts %s for %s', discounts, self)

        self.discounts = discounts


class DiscountedCartMixin(CalculatedOrderDiscountMixin,
                          DiscountedCartBase):
    """
    Mixin class for `Cart` objects which have their discount calculated.
    """
    class Meta:
        abstract = True


class DiscountedCartItemMixin(CalculatedItemDiscountMixin,
                              DiscountedCartItemBase):
    """
    Mixin class for `Cart` objects which have their discount calculated.
    """
    class Meta:
        abstract = True

class DiscountedOrderMixin(PersistentDiscountedItemBase,
                           DiscountedOrderBase,
                           CalculatedOrderDiscountMixin):
    """
    Mixin class for `Order` objects which have their discount calculated.
    """
    class Meta:
        abstract = True


class DiscountedOrderItemMixin(CalculatedItemDiscountMixin,
                               PersistentDiscountedItemBase,
                               DiscountedOrderItemBase):
    """
    Mixin class for `OrderItem` objects which have their discount calculated.
    """
    class Meta:
        abstract = True


class AccountedDiscountedItemMixin(object):
    """
    Model mixin class for orders for which the use is automatically accounted
    upon confirmation.
    """
    def confirm(self):
        """
        Register discount usage.
        """

        # Call registration for superclass
        super(AccountedDiscountedItemMixin, self).confirm()

        # Make sure we're of the proper type so we have a discounts property
        assert isinstance(self, PersistentDiscountedItemBase)

        discount_class = get_model_from_string(DISCOUNT_MODEL)

        discounts = self.discounts.all()

        # Register discount usage for order
        discount_class.register_use(discounts)


class DiscountCouponMixin(models.Model):
    """
    Model mixin class for orders or cart for which discounts are calculated based
    on a given coupon code.
    """

    class Meta:
        abstract = True

    coupon_code = models.CharField(verbose_name=_('coupon code'), null=True,
                                   max_length=COUPON_LENGTH, blank=True)
    """ Coupon code entered for the current order. """

    def get_valid_discounts(self, **kwargs):
        """ Return valid discounts for the current order. """
        superclass = super(DiscountCouponMixin, self)
        return superclass.get_valid_discounts(coupon_code=self.coupon_code,
                                              **kwargs)


class DiscountCouponItemMixin(models.Model):
    """
    Model mixin class for order or cart items for which discounts are
    calculated based on a coupon code.
    """
    class Meta:
        abstract = True

    def get_valid_discounts(self, **kwargs):
        """ Return valid discounts for the current item. """
        superclass = super(DiscountCouponItemMixin, self)

        # Get cart or order
        parent = self.get_parent()

        return superclass.get_valid_discounts(coupon_code=parent.coupon_code,
                                              **kwargs)

