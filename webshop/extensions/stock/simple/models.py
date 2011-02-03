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

from django.db import models
from django.utils.translation import ugettext_lazy as _

from webshop.extensions.stock.models import StockedCartItemMixinBase
from webshop.extensions.stock.simple.settings import STOCK_CHOICES, \
                                                     STOCK_DEFAULT, \
                                                     STOCK_ORDERABLE

class StockedCartItemMixin(StockedCartItemMixinBase):
    """
    Mixin class for shopping carts containing items which can be out of stock.
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
    
    def is_available(self):
        """
        Determine whether or not this item is available.
        """
        
        return self.get_stocked_item().is_available()


class StockedItemMixin(models.Model):
    """
    Item with a simple stock selection mechanism: the possible options for
    the available `stock` field signify certain stock states, some of which
    correspond to an item being orderable.
    
    This could be associated with a `Product`, a `Variation` or some other
    property that pertains to the specific state of 
    :class:`CartItemBase <webshop.core.models.CartItemBase>` subclasses.
    """

    class Meta:
        abstract = True

    stock = models.SmallIntegerField(_('stock'), choices=STOCK_CHOICES,
                                     default=STOCK_DEFAULT)
    """
    SmallIntegerField allowing for choices from `STOCK_CHOICES`, with a
    default value of `STOCK_DEFAULT`.
    """

    def is_available(self):
        """
        Method used to determine whether or not the current item is in an
        orderable state.
        """
        if self.stock in STOCK_ORDERABLE:
            return True

        return False

