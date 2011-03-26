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

from webshop.extensions.stock.exceptions import NoStockAvailableException


class StockedCartItemBase(object):
    """
    Base class for cart items for which the stock can be maintained.
    By default the `is_available` method returns `True`, this method can be
    overridden in subclassed to provide for more extended functionality.

    .. todo::
        Decide whether this bugger belongs into :module:webshop.core or
        whether it is just fine at it's place right here.

        * Pro: We'll have a generic API for determining the stock state of
          items.
        * Con: It's bad to have too much code in the core, it is better if
          modules within `django-webshop` have the least possible knowledge
          about one another.

    """

    def is_available(self, quantity):
        """
        The `is_available` method can be used to determine whether a cart
        item is eligible to be saved or not.
        """
        return True


class StockedCartBase(object):
    """
    Base class for shopping carts for which stock is kept.
    """

    def add_item(self, product, quantity=1, **kwargs):
        """
        Attempt to add item to cart.

        This method will raise a :class:`NoStockAvailableException` when
        no stock items are available.
        """

        # Stock is available, just return the superclass value
        cartitem = super(StockedCartBase, self).add_item(product,
                                                         quantity,
                                                         **kwargs)

        # Check whether enough stock is available
        if not cartitem.is_available(cartitem.quantity):
            # Substract the quantity again. Inefficient but necessary for now
            cartitem.quantity -= quantity
            cartitem.save()

            # Raise error
            raise NoStockAvailableException(item=self)

        return cartitem

class StockedOrderItemBase(object):
    """
    Mixin base class for `OrderItem`'s containing items for which stock is kept.
    """
    def check_stock(self):
        """
        Check whether the stock for the current order item is available.
        This should be called right before `register_confirmation`.
        """
        if not self.is_available(self.quantity):
            raise NoStockAvailableException(item=self)

    def prepare_confirm(self):
        """
        Extend confirmation preparation by checking whether stock is
        available for this order.

        :raises: NoStockAvailableException
        """

        super(StockedOrderItemBase, self).prepare_confirm()
        self.check_stock()

    def confirm(self):
        """
        Before registering confirmation, first make sure enough stock is
        available. This should have already been checked when adding the
        product to the shopping cart but who knows: somebody might have
        already bought the product in the meanwhile.

        For this to work well, it is important that this
        `register_confirmation` function is called before that of discounts
        and other possible accounting functions.
        """

        # Check whether enough stock is available
        assert self.is_available(self.quantity), \
            'No stock available, you should have called `prepare_confirm()`.'

        super(StockedOrderItemBase, self).confirm()


class StockedOrderBase(object):
    """
    Mixin base class for `Order`'s with items for which stock is kept.
    """
    def check_stock(self):
        """ Check the stock for all items in this order. """
        for item in self.get_items():
            item.check_stock()
