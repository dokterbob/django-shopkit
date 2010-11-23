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

from webshop.core.settings import PRODUCT_MODEL, CART_MODEL, ORDER_MODEL
from webshop.core.managers import ActiveProductManager
from webshop.core.basemodels import AbstractPricedItemBase, NamedItemBase, \
                                    QuantizedItemBase


""" Abstract base models for essential shop components. """

class ProductBase(AbstractPricedItemBase):
    """ Abstract base class for products in the webshop. """

    class Meta(AbstractPricedItemBase.Meta):
        verbose_name = _('product')
        verbose_name_plural = ('products')
        abstract = True
    
    objects = models.Manager()
    in_shop = ActiveProductManager()
    """ ActiveProductManager returning only products with `active=True`. """
    
    active = models.BooleanField(verbose_name=_('active'),
                                 help_text=_('Product active in webshop.'),
                                 default=True)
    """ Whether the product is active in the webshop frontend. """


class CartItemBase(AbstractPricedItemBase, QuantizedItemBase):
    """ Abstract base class for shopping cart items. """

    class Meta(AbstractPricedItemBase.Meta):
        verbose_name = _('cart item')
        verbose_name_plural = _('cart items')
        abstract = True
        unique_together = ('cart', 'product')


    cart = models.ForeignKey(CART_MODEL)
    """ Shopping cart this item belongs to. """
    
    product = models.ForeignKey(PRODUCT_MODEL)
    """ Product associated with this shopping cart item. """


class CartBase(AbstractPricedItemBase):
    """ Abstract base class for shopping carts. """

    class Meta(AbstractPricedItemBase.Meta):
        verbose_name = _('cart')
        verbose_name_plural = _('carts')
        abstract = True


class OrderItemBase(AbstractPricedItemBase, QuantizedItemBase):
    """ Abstract base class for order items. """

    class Meta(AbstractPricedItemBase.Meta):
        verbose_name = _('order item')
        verbose_name_plural = _('order items')
        abstract = True
        unique_together = ('order', 'product')


    order = models.ForeignKey(ORDER_MODEL)
    """ Order this item belongs to. """
    
    product = models.ForeignKey(PRODUCT_MODEL)
    """ Product associated with this order item. """


class OrderBase(AbstractPricedItemBase):
    """ Abstract base class for orders. """

    class Meta(AbstractPricedItemBase.Meta):
        verbose_name = _('order')
        verbose_name_plural = _('orders')
        abstract = True


class PaymentBase(models.Model):
    """ Abstract base class for payments. """
    
    order = models.ForeignKey(ORDER_MODEL)
    """ Order this payment belongs to. """

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')
        abstract = True


