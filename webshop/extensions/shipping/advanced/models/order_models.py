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

        assert 'order_methods' in kwargs or 'item_methods' in kwargs, \
            'We need either a restriction to order shipping methods or '+ \
            'item shipping methods in order to find the cheapest method.'

        shipping_method_class = get_model_from_string(SHIPPING_METHOD_MODEL)

        shipping_address = getattr(self, 'shipping_address', None)
        if not 'country' in kwargs and shipping_address:
            assert self.shipping_address.country

            country = self.shipping_address.country

            logger.debug(u'Using country %s to find cheapest shipping method for %s',
                         country, self)

            kwargs['country'] = country

        shipping_method = shipping_method_class.get_cheapest(**kwargs)

        logger.debug(u'Found shipping method %s for %s', shipping_method, self)

        return shipping_method


class CalculatedShippingItemMixin(object):
    def get_shipping_method(self, **kwargs):
        superclass = super(CalculatedShippingItemMixin, self)

        price = self.get_price_without_shipping()

        method = superclass.get_shipping_method(item_methods=True,
                                                item_price=price)

        return method

    def get_total_shipping_costs(self, **kwargs):
        method = self.get_shipping_method(**kwargs)

        if method:
            costs = method.get_cost()
            logger.info(u'Shipping method %s found for object %s with args %s',
                        method, self, kwargs)

        else:
            logger.info(u'No shipping method found for kwargs %s and object %s',
                        kwargs, self)

            costs = Decimal('0.00')

        assert isinstance(costs, Decimal)

        return costs

class CalculatedShippingOrderMixin(CalculatedShippingItemMixin):
    def get_shipping_method(self, **kwargs):
        superclass = super(CalculatedShippingItemMixin, self)

        price = self.get_price_without_shipping()

        method = superclass.get_shipping_method(order_methods=True,
                                                order_price=price)

        return method

    def get_order_shipping_costs(self, **kwargs):
        superclass = super(CalculatedShippingOrderMixin, self)
        return superclass.get_total_shipping_costs()


class PersistentShippedItemBase(models.Model):
    """
    Mixin class for `Order`'s and `OrderItem`'s for which the shipping method
    is stored persistently upon calling the `update_shipping` method.
    """

    class Meta:
        abstract = True

    shipping_method = models.ForeignKey(SHIPPING_METHOD_MODEL,
                                        verbose_name=_('shipping method'),
                                        null=True, blank=True)

    def update_shipping(self):
        """
        Call `update_shipping` on the superclass and get the shipping method,
        store the resulting `ShippingMethod` on the `shipping_method`
        property.
        """

        super(PersistentShippedItemBase, self).update_shipping()

        assert self.pk, 'Object not saved, need PK for assigning method'

        method = self.get_shipping_method()

        assert self.get_shipping_costs() == Decimal('0.00') or \
            (self.get_shipping_costs() and method)

        logger.debug(u'Storing shipping method %s for %s', method, self)

        self.shipping_method = method


class ShippedCartMixin(CalculatedShippingOrderMixin, CheapestShippingMixin, ShippedCartBase):
    """ Base class for shopping carts with shippable items. """
    class Meta:
        abstract = True


class ShippedCartItemMixin(CalculatedShippingItemMixin, CheapestShippingMixin, ShippedCartItemBase):
    """ Base class for shopping cart items which are shippable. """
    class Meta:
        abstract = True


class ShippedOrderMixin(PersistentShippedItemBase,
                        ShippedOrderBase,
                        CalculatedShippingOrderMixin,
                        CheapestShippingMixin):
    """ Base class for orders with a shipping_method. """

    class Meta:
        abstract = True


class ShippedOrderItemMixin(PersistentShippedItemBase,
                            CalculatedShippingItemMixin,
                            CheapestShippingMixin,
                            ShippedOrderItemBase):
    """
    Base class for orderitems which can have individual shipping costs
    applied to them.
    """

    class Meta:
        abstract = True
