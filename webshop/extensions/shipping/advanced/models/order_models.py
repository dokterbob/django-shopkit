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
from webshop.core.utils import get_model_from_string

from webshop.extensions.shipping.advanced.settings import \
    SHIPPING_METHOD_MODEL

from webshop.extensions.shipping.basemodels import \
    ShippedCartBase, ShippedCartItemBase, \
    ShippedOrderBase, ShippedOrderItemBase


class AutomaticShippingMixin(object):
    """
    Mixin class for shippable items for which the choice of method is
    automatic.
    """

    def get_shipping_method(self, **kwargs):
        """
        Return the shipping method used for the current item. This method
        should be overridden in subclasses. It should return `None` if
        shipping is not applicable for this item and hence, the shipping
        costs should be 0.
        """
        raise NotImplementedError


class CheapestShippingMixin(AutomaticShippingMixin):
    """ Shippable item which defaults to using the """

    def get_shipping_method(self, **kwargs):
        """
        Return the cheapest shipping method or an order or item.

        .. todo::
            This code is probably a bit too low-level.
        """

        assert 'order_methods' in kwargs or 'items_methods' in kwargs, \
            'We need either a restriction to order shipping methods or \
             item shipping methods in order to find the cheapest method.'

        shipping_method_class = get_model_from_string(SHIPPING_METHOD_MODEL)

        shipping_method = shipping_method_class.get_cheapest(**kwargs)

        return shipping_method

class CalculatedShippingItemMixin(object):
    def get_shipping_method(self, **kwargs):
        superclass = super(CalculatedShippingOrderMixin, self)

        method = superclass.get_shipping_method(item_methods=True)

        return method

    def get_shipping_costs(self, **kwargs):
       return self.get_shipping_method(**kwargs).get_cost()

class CalculatedShippingOrderMixin(CalculatedShippingItemMixin):
    def get_shipping_method(self, **kwargs):
        superclass = super(CalculatedShippingOrderMixin, self)

        method = superclass.get_shipping_method(order_methods=True)

        return method

    def get_order_shipping_costs(self, **kwargs):
        superclass = super(CalculatedShippingOrderMixin, self)
        return superclass.get_shipping_costs()

# class CalculatedShippingOrderMixin(CalculatedShippingMixin):
#     def get_valid_shipping_methods(self, **kwargs):
#         """ Return valid shipping_methods for the current order. """
#         superclass = super(ShippedCartMixin, self)
#         return superclass.get_valid_shipping_methods(order_methods=True,
#                                                      **kwargs)
#
# def get_shipping_costs(self, **kwargs):
#     """
#     Return the shipping costs for the current item, based on the
#     shipping method returned by `get_shipping_method`. If `None` was
#     returned, the shipping costs are `Decimal('0.0')`.
#     """
#
#     method = self.get_shipping_method(**kwargs)
#     if method:
#         return method.get_cost()
#
#     return Decimal('0.00')


# class CalculatedOrderShippingMixin(object):
# class CheapestShippableItemMixin(object):
#

class ShippedCartMixin(CalculatedShippingOrderMixin, ShippedCartBase):
    """ Base class for shopping carts with shippable items. """
    class Meta:
        abstract = True

    def get_valid_shipping_methods(self, **kwargs):
        """ Return valid shipping_methods for the current order. """
        superclass = super(ShippedCartMixin, self)
        return superclass.get_valid_shipping_methods(order_methods=True,
                                                     **kwargs)


class ShippedCartItemMixin(CalculatedShippingItemMixin, ShippedCartItemBase):
    """ Base class for shopping cart items which are shippable. """
    class Meta:
        abstract = True

    def get_valid_shipping_methods(self, **kwargs):
        """ Return valid shipping_methods for the current order item. """
        superclass = super(ShippedCartItemMixin, self)
        return superclass.get_valid_shipping_methods(item_methods=True,
                                                     product=self.product,
                                                     **kwargs)


class ShippedOrderMixin(CalculatedShippingOrderMixin, ShippedOrderBase):
    """ Base class for orders with a shipping_method. """

    class Meta:
        abstract = True

    def get_valid_shipping_methods(self, **kwargs):
        """ Return valid shipping_methods for the current order. """
        superclass = super(ShippedOrderMixin, self)
        return superclass.get_valid_shipping_methods(order_methods=True,
                                                     **kwargs)


class ShippedOrderItemMixin(CalculatedShippingItemMixin, ShippedOrderItemBase):
    """
    Base class for orderitems which can have individual shipping costs
    applied to them.
    """

    class Meta:
        abstract = True

    def get_valid_shipping_methods(self, **kwargs):
        """ Return valid shipping_methods for the current order item. """
        superclass = super(ShippedCartItemMixin, self)
        return superclass.get_valid_shipping_methods(item_methods=True,
                                                     product=self.product,
                                                     **kwargs)
