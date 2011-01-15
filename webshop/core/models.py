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

from django.contrib.auth.models import User

from django.utils.translation import ugettext_lazy as _
from django.db import models

from webshop.core.settings import PRODUCT_MODEL, CART_MODEL, \
                                  CARTITEM_MODEL, ORDER_MODEL, \
                                  CUSTOMER_MODEL
from webshop.core.managers import ActiveProductManager
from webshop.core.basemodels import AbstractPricedItemBase, NamedItemBase, \
                                    QuantizedItemBase, AbstractCustomerBase

from webshop.core.util import get_model_from_string


""" Abstract base models for essential shop components. """

class UserCustomerBase(AbstractCustomerBase, User):
    """ Abstract base class for customers which can also be Django users. """
    
    class Meta(AbstractCustomerBase.Meta):
        abstract = True
    
    # 
    # def __unicode__(self):
    #     """ Unicode representation of a UserCustomer is the representation of the
    #         user, if one has been set. Otherwise, return the primary key of self 
    #         instaed.
    #     """
    #     if self.user:
    #         return unicode(self.user)
    #     
    #     return self.pk


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
    
    def __unicode__(self):
        """ A natural representation for a cart item is the product. """
        
        return unicode(self.product)
    
    def get_price(self, **kwargs):
        """ Wraps `get_total_price()`. """
        
        return self.get_total_price(**kwargs)
    
    def get_total_price(self, **kwargs):
        """ Gets the tatal price for the items in the cart. """
        
        return self.quantity*self.get_piece_price(**kwargs)
    
    def get_piece_price(self, **kwargs):
        """ Gets the price per piece for a given quantity of items. """
        
        return self.product.get_price(quantity=self.quantity, **kwargs)


class CartBase(AbstractPricedItemBase):
    """ Abstract base class for shopping carts. """

    class Meta(AbstractPricedItemBase.Meta):
        verbose_name = _('cart')
        verbose_name_plural = _('carts')
        abstract = True
    
    customer = models.ForeignKey(CUSTOMER_MODEL, verbose_name=('customer'), null=True)
    """ Customer who owns this cart, if any. """
    
    def getCartItems(self):
        """ Gets all items from the cart with a quantity > 0. """
        
        return self.cartitem_set.filter(quantity__gt=0)
    
    def getCartItem(self, product):
        """ Either instantiates and returns a CartItem for the 
            Cart-Product combination or fetches it from the
            database. The creation is lazy: the resulting CartItem
            is not automatically saved. """
        
        # It makes more sense to execute this code on a higher level
        # instead of everytime a cart item is requested.
        cartitem_class = get_model_from_string(CARTITEM_MODEL)
        
        # Note that we won't use 'get_or_create' here as it automatically
        # saves the object.
        try:
            cartitem = cartitem_class.objects.get(cart=self, 
                                                  product=product)
            
            logger.debug('Found existing cart item for product \'%s\'' % product)
            
        except cartitem_class.DoesNotExist:
            logger.debug('Product \'%s\' not already in Cart, creating new item.' % product)

            cartitem = cartitem_class(cart=self,
                                      product=product)
        
        return cartitem
        
    def addProduct(self, product, quantity=1):
        """ Adds the specified product in the specified quantity
            to the current shopping Cart. This effectively creates
            a CartItem for the Product-Cart combination or updates
            it when a CartItem already exists.
            
            It returns an _unsaved_ instance of a CartItem, so the
            called is able to determine whether the product was already
            in the shopping cart or not. 
        """
        assert isinstance(quantity, int), 'Quantity not an integer.'
        
        cartitem = self.getCartItem(product)
        
        # We can do this without querying the actual value from the 
        # database.
        # cartitem.quantity = models.F('quantity') + quantity
        cartitem.quantity += quantity
        
        return cartitem
    
    def get_total_items(self):
        """ Gets the total quantity of products in the shopping cart. """
        
        quantity = 0
        
        # TODO: Use aggregation
        for cartitem in self.getCartItems():
            quantity += cartitem.quantity
        
        return quantity
    
    def get_price(self, **kwargs):
        """ Wraps the `get_total_price` function. """
        
        return self.get_total_price(**kwargs)
    
    def get_total_price(self, **kwargs):
        """ Gets the total price for all items in the cart. """
        
        logger.debug('Calculating total price for shopping cart.')
        
        # logger.debug(self.getCartItems()[0].get_total_price())
        
        # TODO: Add either caching or aggregation. Preferably the former.
        # This can be achieved by keeping something like a serial or timestamp
        # in the Cart and CartItem models.
        price = Decimal("0.0")
        
        for cartitem in self.getCartItems():
            item_price = cartitem.get_total_price(**kwargs)
            logger.debug('Adding price %f for item \'%s\' to total cart price.' % \
                (item_price, cartitem))
            price += item_price
        
        return price


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
    
    @classmethod
    def fromCartItem(cls, cartitem, order):
        """ Create an order item from a shopping cart item. """
        
        orderitem = cls(product=cartitem.product, 
                        quantity=cartitem.quantity,
                        order=order)
                
        # We should consider iterating over all the fields (properties)
        # of the cartitem and copying the information to the order item.
        #
        # However, we need to skip AutoField instances in any case.
        #
        # Also: we should read all properties - not just fields - from the
        # CartItem and see whether matching fields exist for the OrderItem.

        cartitem_keys = cartitem.__dict__.keys()
        orderitem_fields = cls._meta.fields
        
        from django.db.models.fields import AutoField

        for orderitem_field in orderitem_fields:
            # Skip AutoField instances
            if not isinstance(orderitem_field, AutoField):            
                attname = orderitem_field.attname
                
                if attname in cartitem_keys:
                     cartitem_value = cartitem[attname]
                     
                     setattr(orderitem, attname, cartitem_value)            
        
        orderitem.save()
        
        return orderitem


class OrderBase(AbstractPricedItemBase):
    """ Abstract base class for orders. """

    class Meta(AbstractPricedItemBase.Meta):
        verbose_name = _('order')
        verbose_name_plural = _('orders')
        abstract = True

    customer = models.ForeignKey(CUSTOMER_MODEL, verbose_name=('customer'))
    """ Customer whom this order belongs to. """

    @classmethod
    def fromCart(cls, cart, customer):
        """ Instantiate an order based on the basis of a
            shopping cart, copying all the items. """
        order = cls(customer=customer)
        order.save()
        
        # TODO
        # We should copy any eventual matching fields from the
        # cart into the order.

        orderitem_class = get_model_from_string(ORDERITEM_MODEL)
        
        for cartitem in cart.cartitem_set.all():
            orderitem = orderitem_class.fromCartItem(cartitem=cartitem,
                                                     order=order)
            
            assert orderitem, 'Something went wrong creating an \
                               OrderItem from a CartItem.'
        
        
        return order



class PaymentBase(models.Model):
    """ Abstract base class for payments. """
    
    order = models.ForeignKey(ORDER_MODEL)
    """ Order this payment belongs to. """

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')
        abstract = True


