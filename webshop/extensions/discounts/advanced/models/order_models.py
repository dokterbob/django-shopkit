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


class CalculatedOrderDiscountMixin(object):
    """
    Base class for orders or carts for which the discount is the
    order discount is calculated rather than retrieved from persistent
    storage.
    """

    def get_valid_discounts(self, **kwargs):
        """ Return valid discounts for the current order. """
        superclass = super(CalculatedOrderDiscountMixin, self)
        return superclass.get_valid_discounts(order_discounts=True, **kwargs)

    def get_order_discount(self, **kwargs):
        """
        Get the discount specific for this `Order`.
        """

        # Now, add discounts on the total order
        valid_discounts = self.get_valid_discounts(**kwargs)
        price = self.get_price(**kwargs)

        total_discount = Decimal('0.00')
        for discount in valid_discounts:
            total_discount += discount.get_discount(order_price=price,
                                                    **kwargs)

        return total_discount


class DiscountCouponMixin(models.Model):
    """
    Mixin class for orders or cart for which discounts are calculated based
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


class CalculatedItemDiscountMixin(object):
    """
    Base class for order or cart items for which the discount is
    calculated rather than retrieved from persistent storage.
    """

    def get_valid_discounts(self, **kwargs):
        """ Return valid discounts for the current order. """
        superclass = super(CalculatedItemDiscountMixin, self)
        return superclass.get_valid_discounts(product=self.product,
                                              item_discounts=True,
                                              **kwargs)


    def get_total_discount(self, **kwargs):
        """
        Get the total discount for this OrderItem.
        """

        valid_discounts = self.get_valid_discounts(**kwargs)
        price = self.get_price(**kwargs)

        total_discount = Decimal('0.00')
        for discount in valid_discounts:
            total_discount += discount.get_discount(item_price=price, \
                                                    **kwargs)

        return total_discount
