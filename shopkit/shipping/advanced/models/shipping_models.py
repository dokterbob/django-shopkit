# Copyright (C) 2010-2011 Mathijs de Bruin <mathijs@mathijsfietst.nl>
#
# This file is part of django-shopkit.
#
# django-shopkit is free software; you can redistribute it and/or modify
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
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

# Get the currently configured currency field, whatever it is
from shopkit.currency.utils import get_currency_field
PriceField = get_currency_field()


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

        return cls.objects.all()

    def is_valid(self, **kwargs):
        """
        Check to see whether an individual method is valid under the
        given circumstances.
        """

        valid = self.get_valid_methods(**kwargs)

        assert self.pk, \
        "This method has not yet been saved, which is required in order \
         to determine it's validity (for now)."

        valid.filter(pk=self.pk)

        return valid.exists()


    def get_cost(self, **kwargs):
        """
        Get the total shipping costs resulting from this `ShippingMethod`.
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

        superclass = super(OrderShippingMethodMixin, cls)
        valid = superclass.get_valid_methods(**kwargs)

        if not order_methods is None:
            # If an order methods criterium has been specified
            valid = valid.filter(order_cost__isnull=not order_methods)

        logger.debug(u'Valid order shipping methods for kwargs %s: %s',
                     kwargs, valid)

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

            cheapest = shipping_methods.order_by('order_cost')[0]

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

        superclass = super(ItemShippingMethodMixin, cls)
        valid = superclass.get_valid_methods(**kwargs)

        if not item_methods is None:
            # If an item methods criterium has been specified
            valid = valid.filter(item_cost__isnull=not item_methods)

        logger.debug(u'Valid item shipping methods for kwargs \'%s\': %s',
                     kwargs, valid)

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

            cheapest = shipping_methods.order_by('item_cost')[0]

            return cheapest
        else:
            # Try and see whether
            try:
                return super(ItemShippingMethodMixin, self).get_cheapest(**kwargs)
            except AttributeError:
                return None

    def get_cost(self, **kwargs):
        return self.item_cost


class MinimumOrderAmountShippingMixin(models.Model):
    """ Shipping mixin for methods valid only from a specified order amount. """

    class Meta:
        abstract = True

    minimal_order_price = PriceField(verbose_name=_('minimal order amount'),
                                     blank=True, null=True, db_index=True)

    @classmethod
    def get_valid_methods(cls, order_price=None, **kwargs):
        """
        Return shipping methods for which the order price is above the
        minimal order price or ones for which no minimal order price has
        been specified.

        :param order_price: Price for the current order, used to determine
                            valid shipping methods.
        """
        superclass = super(MinimumOrderAmountShippingMixin, cls)

        valid = superclass.get_valid_methods(**kwargs)

        valid_no_min = valid.filter()

        if order_price:
            # Return methods for which the minimal order price is less
            # than the current `order_price` or ones for which a minimal
            # order price does not apply.
            valid = valid.filter(Q(minimal_order_price__lte=order_price) | \
                                 Q(minimal_order_price__isnull=True))
        else:
            # Return methods for which no minimal order price is specified
            valid = valid.filter(minimal_order_price__isnull=True)

        return valid


class MinimumItemAmountShippingMixin(models.Model):
    """ Shipping mixin for methods valid only from a specified order amount. """

    class Meta:
        abstract = True

    minimal_item_price = PriceField(verbose_name=_('minimal item amount'),
                                     blank=True, null=True, db_index=True)

    @classmethod
    def get_valid_methods(cls, item_price=None, **kwargs):
        """
        Return shipping methods for which the item price is above a
        minimum price or ones for which no minimal item price has
        been specified.

        :param item_price: Price for the current `OrderItem`, used to
                           determine valid shipping methods.
        """
        superclass = super(MinimumItemAmountShippingMixin, cls)

        valid = superclass.get_valid_methods(**kwargs)

        if item_price:
            # Return methods for which the minimal order price is less
            # than the current `order_price` or ones for which a minimal
            # order price does not apply.
            valid = valid.filter(Q(minimal_item_price__lte=item_price) | \
                                 Q(minimal_item_price__isnull=True))
        else:
            # Return methods for which no minimal order price is specified
            valid = valid.filter(minimal_item_price__isnull=True)

        return valid
