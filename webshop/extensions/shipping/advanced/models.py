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

# Get the currently configured currency field, whatever it is
from webshop.extensions.currency.utils import get_currency_field
PriceField = get_currency_field()

from webshop.extensions.shipping.models import *
from webshop.extensions.shipping.advanced.settings import *


class ShippableItemMixin(AbstractPricedItemBase):
    """ Mixin class for shippable items. """

    def get_valid_shipping_methods(self, **kwargs):
        """
        Return all available shipping methods for the current item. By default
        this returns *all* shipping methods, so subclasses should act as a
        filter on this.
        """
        shipping_method_class = get_model_from_string(SHIPPING_METHOD_MODEL)

        shipping_methods = shipping_method_class.get_valid_shipping_methods(**kwargs)

        return shipping_methods

    def get_shipping_method(self, **kwargs):
        """
        Return the shipping method used for the current item. This method
        should be overridden in subclasses. It should return `None` if
        shipping is not applicable for this item and hence, the shipping
        costs should be 0.
        """
        raise NotImplementedError

    def get_shipping_cost(self, **kwargs):
        """
        Return the shipping costs for the current item, based on the
        shipping method returned by `get_shipping_method`. If `None` was
        returned, the shipping costs are `Decimal('0.0')`.
        """

        method = self.get_shipping_method(**kwargs)
        if method:
            return method.get_cost()

        return Decimal('0.0')

    def get_price_with_shipping(self, **kwargs):
        """ Get the current price with shipping method added. applied. """

        return self.get_price(**kwargs) + self.get_shipping_cost(**kwargs)


class CheapestShippableItemMixin(object):
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


class ShippableOrderBase(ShippableItemMixin, models.Model):
    """ Base class for orders with a shipping_method. """

    class Meta:
        abstract = True

    def get_valid_shipping_methods(self, **kwargs):
        """ Return valid shipping_methods for the current order. """
        superclass = super(ShippableOrderBase, self)
        return superclass.get_valid_shipping_methods(order_methods=True,
                                                     **kwargs)

    def get_shipping_cost(self, **kwargs):
        """
        Return the total shipping costs for this order. This sums up
        total costs for the order with the costs for individual items.
        """

        superclass = super(ShippableOrderBase, self)

        shipping_cost = superclass.get_shipping_cost(**kwargs)

        for item in self.orderitem_set.all():
            shipping_cost += item.get_shipping_cost()

        return shipping_cost


class ShippableOrderItemBase(ShippableItemMixin, models.Model):
    """
    Base class for orderitems which can have individual shipping costs
    applied to them.
    """

    class Meta:
        abstract = True

    def get_valid_shipping_methods(self, **kwargs):
        """ Return valid discounts for the current order. """
        superclass = super(ShippableOrderItemBase, self)
        return superclass.get_valid_shipping_methods(product=self.product,
                                                     order_methods=True,
                                                     **kwargs)


class ShippingMethodBase(models.Model):
    """ Base class for shipping methods. """

    class Meta:
        abstract = True

    @classmethod
    def get_valid_methods(cls, **kwargs):
        """
        Get all valid shipping methods for a given `kwargs`. By default,
        all methods are valid.
        """

        raise cls.objects.all()


    def is_valid(self, **kwargs):
        """
        Check to see whether an individual method is valid under the
        given circumstances.
        """

        valid = self.get_valid_discounts(**kwargs)

        assert self.pk, \
        "This method has not yet been saved, which is required in order \
         to determine it's validity (for now)."

        valid.filter(pk=self.pk)

        return valid.exists()


    def get_shipping_cost(self, **kwargs):
        """
        Get the total shipping costs resulting from by this `ShippingMethod`.
        This method should be implemented by subclasses of
        `:class:ShippingMethodBase`.
        """
        raise NotImplementedError


class OrderShippingMethodMixin(models.Model):
    """
    Mixin for shipping methods which process whole orders and not
    individual items.
    """

    class Meta:
        abstract = True

    order_cost = PriceField(verbose_name=_('order shipping cost'),
                            null=True, blank=True)
    """
    Total shipping cost for orders for which this method applies.

    .. todo::
        Make design decision: should null=blank=True here?
    """

    @classmethod
    def get_valid_methods(cls, order_methods=None, **kwargs):
        """
        We want to be able to discriminate between methods valid for
        the whole order and those valid for order items.

        :param order_methods: When `True`, only items for which
                               `order_cost` has been specified are valid.
                               When `False`, only items which have no
                               `order_cost` specified are let through.
        """

        superclass = super(OrderShippingMethodMixin, self)
        valid = superclass.get_valid_discounts(**kwargs)

        if not order_methods is None:
            # If an order methods criterium has been specified
            valid = valid.filter(order_cost__isnull=not order_methods)

        return valid

    @classmethod
    def get_cheapest(self, **kwargs):
        """
        Return the cheapest order shipping method if `order_methods` is
        specified. Return whatever it is the superclass returns otherwise.
        """

        # This only makes sense if order_methods are specified
        if kwargs.get('order_methods', None):
            shipping_methods = self.get_valid_methods(**kwargs)

            if not shipping_methods.exists():
                return None

            cheapest = shipping_methods.order_by('-order_cost')[0]

            return cheapest
        else:
            # Try and see whether
            try:
                return super(OrderShippingMethodMixin, self).get_cheapest(**kwargs)
            except AttributeError:
                return None

    def get_cost(self, **kwargs):
        return self.order_cost


class ItemShippingMethodMixin(models.Model):
    """
    Mixin for shipping methods which process individual items and not
    whole orders.
    """

    class Meta:
        abstract = True

    item_cost = PriceField(verbose_name=_('item shipping cost'),
                            null=True, blank=True)
    """
    Total shipping cost for items for which this method applies.

    .. todo::
        Make design decision: should null=blank=True here?
    """

    @classmethod
    def get_valid_methods(cls, item_methods=None, **kwargs):
        """
        We want to be able to discriminate between methods valid for
        the whole item and those valid for item items.

        :param item_methods: When `True`, only items for which
                               `item_cost` has been specified are valid.
                               When `False`, only items which have no
                               `item_cost` specified are let through.
        """

        superclass = super(ItemShippingMethodMixin, self)
        valid = superclass.get_valid_discounts(**kwargs)

        if not item_methods is None:
            # If an item methods criterium has been specified
            valid = valid.filter(item_cost__isnull=not item_methods)

        return valid

    @classmethod
    def get_cheapest(self, **kwargs):
        """
        Return the cheapest shipping method or `None`.

        If `item_cost` is not specified, an attempt will be made to call
        `get_cheapest` on the superclass. If this method does not exist in
        the superclass, `None` is returned.
        """
        if kwargs.get('item_methods', None):
            # We can only find item_methods here.
            shipping_methods = self.get_valid_methods(**kwargs)

            if not shipping_methods.exists():
                return None

            cheapest = shipping_methods.order_by('-item_cost')[0]

            return cheapest
        else:
            # Try and see whether
            try:
                return super(ItemShippingMethodMixin, self).get_cheapest(**kwargs)
            except AttributeError:
                return None

    def get_cost(self, **kwargs):
        return self.item_cost

