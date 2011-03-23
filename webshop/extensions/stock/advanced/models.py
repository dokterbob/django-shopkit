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

from webshop.extensions.stock.models import StockedCartItemBase, \
                                            StockedCartBase, \
                                            StockedOrderItemBase


class StockedItemBase(object):
    """
    Generic base class for `CartItem`'s or `OrderItem`'s for which the stock
    is represented by a stocked item somehow.
    """
    def get_stocked_item(self):
        """
        Get the :class:`StockedItemMixin <websop.extensions.simple.StockedItemMixin>`
        subclass instance whose `is_available` method should determine whether
        we are out of stock.

        This method
        should be overridden in order to be able to specify whether the cart
        item is available or not.
        """

        raise NotImplementedError

    def is_available(self, quantity):
        """
        Determine whether or not this item is available.
        """
        return self.get_stocked_item().is_available(quantity)


class StockedCartItemMixin(StockedItemBase, StockedCartItemBase):
    """
    Mixin class for `CartItem`'s containing items for which stock is kept.
    """
    pass

class StockedCartMixin(StockedCartBase):
    """
    Mixin class for `Cart`'s containing items for which stock is kept.
    """
    pass

class StockedOrderItemMixin(StockedItemBase, StockedOrderItemBase):
    """
    Mixin class for `OrderItem`'s containing items for which stock is kept.
    """

    def register_confirmation(self):
        """
        Register lowering of the current item's stock.
        """

        super(StockedOrderItemMixin, self).register_confirmation()

        stocked_item = self.get_stocked_item()

        logger.debug('Lowering stock of %d for %s with %d',
                     stocked_item.stock,
                     stocked_item,
                     self.quantity)

        stocked_item.stock -= self.quantity
        stocked_item.save()


class StockedOrderMixin(object):
    """
    Mixin class for `Order`'s containing items for which stock is kept.
    """
    pass

class StockedItemMixin(models.Model, StockedItemBase):
    """
    Item for which stock is kept in an integer `stock` field.
    """

    class Meta:
        abstract = True

    stock = models.PositiveIntegerField(_('stock'))
    """
    SmallIntegerField storing the amount of items in stock.
    """

    def is_available(self, quantity):
        """
        Method used to determine whether or not the current item is in an
        orderable state.
        """
        logger.debug('Checking whether quantity %d of %s is stocked',
                     quantity, self)

        if self.stock >= quantity:
            return True

        return False

