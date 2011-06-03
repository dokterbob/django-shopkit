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
from django.utils.translation import ugettext_lazy as _

from shopkit.extensions.stock.models import \
    StockedCartItemBase, StockedCartBase, StockedOrderItemBase, \
    StockedOrderBase, StockedItemBase
from shopkit.extensions.stock.simple.settings import STOCK_CHOICES, \
                                                     STOCK_DEFAULT, \
                                                     STOCK_ORDERABLE


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
    pass

class StockedOrderMixin(StockedOrderBase):
    """
    Mixin class for `Order`'s containing items for which stock is kept.
    """
    pass


class StockedItemMixin(models.Model, StockedItemBase):
    """
    Item with a simple stock selection mechanism: the possible options for
    the available `stock` field signify certain stock states, some of which
    correspond to an item being orderable.
    
    This could be associated with a `Product`, a `Variation` or some other
    property that pertains to the specific state of 
    :class:`CartItemBase <shopkit.core.models.CartItemBase>` subclasses.
    """

    class Meta:
        abstract = True

    stock = models.PositiveSmallIntegerField(_('stock'), choices=STOCK_CHOICES,
                                             default=STOCK_DEFAULT)
    """
    SmallIntegerField allowing for choices from `STOCK_CHOICES`, with a
    default value of `STOCK_DEFAULT`.
    """

    def is_available(self, quantity=None):
        """
        Method used to determine whether or not the current item is in an
        orderable state.
        """
        logger.debug(u'Checking whether %s is stocked', self)

        if self.stock in STOCK_ORDERABLE:
            return True

        return False

