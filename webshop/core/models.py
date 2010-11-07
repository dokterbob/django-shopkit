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

from decimal import Decimal

from django.utils.translation import ugettext_lazy as _

from django.db import models

from webshop.core.settings import *

from webshop.core.managers import ActiveProductManager


class PricedItemBase(models.Model):
    """ Abstract base class for items with a price. """

    class Meta:
        abstract = True

    def get_price(self, *args, **kwargs):
        """ Get price for the current product.
            
            This method _should_ be implemented in a subclass. """

        raise NotImplementedError

    def get_taxes(self, *args, **kwargs):
        """ Get the taxes for the current product. """

        return Decimal('0.0')

    def get_currency(self, *args, **kwargs):
        """ Get the currency for the current price. """

        raise NotImplementedError


class ProductBase(PricedItemBase):
    """ Abstract base class for products in the webshop. """

    class Meta(PricedItemBase.Meta):
        verbose_name = _('product')
        verbose_name_plural = ('products')
    
    objects = models.Manager()
    in_shop = ActiveProductManager()
    """ ActiveProductManager returning only products with `active=True`. """
    
    active = models.BooleanField(verbose_name=_('active'),
                                 help_text=_('Product active in webshop.'),
                                 default=True)
    """ Whether the product is active in the webshop frontend. """


class NamedProductBase(ProductBase):
    """ Abstract base class for products with a simple name. """
    
    class Meta(ProductBase.Meta):
        pass

    name = models.CharField(max_length=MAX_NAME_LENGTH,
                            verbose_name=_('name'))
    """ Name of the product. """


class CartItemBase(PricedItemBase):
    """ Abstract base class for shopping cart items. """

    class Meta(PricedItemBase.Meta):
        verbose_name = _('cart item')
        verbose_name_plural = _('cart items')

    cart = models.ForeignKey(CART_MODEL)
    product = models.ForeignKey(PRODUCT_MODEL)


class CartBase(PricedItemBase):
    """ Abstract base class for shopping carts. """

    class Meta(PricedItemBase.Meta):
        verbose_name = _('cart')
        verbose_name_plural = _('carts')


class OrderItemBase(PricedItemBase):
    """ Abstract base class for order items. """

    class Meta(PricedItemBase.Meta):
        verbose_name = _('order item')
        verbose_name_plural = _('order items')

    order = models.ForeignKey(ORDER_MODEL)
    product = models.ForeignKey(PRODUCT_MODEL)


class OrderBase(PricedItemBase):
    """ Abstract base class for orders. """

    class Meta(PricedItemBase.Meta):
        verbose_name = _('order')
        verbose_name_plural = _('orders')


class PaymentBase(models.Model):
    """ Abstract base class for payments. """
    
    order = models.ForeignKey(ORDER_MODEL)

    class Meta:
        abstract = True
        verbose_name = _('payment')
        verbose_name_plural = _('payments')


