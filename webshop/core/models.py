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
                                  ORDERITEM_MODEL, CUSTOMER_MODEL, \
                                  ORDERSTATE_CHANGE_MODEL, ORDER_STATES, \
                                  DEFAULT_ORDER_STATE
from webshop.core.basemodels import AbstractPricedItemBase, DatedItemBase, \
                                    QuantizedItemBase, AbstractCustomerBase

from webshop.core.utils import get_model_from_string

# Get the currently configured currency field, whatever it is
from webshop.extensions.currency.utils import get_currency_field
PriceField = get_currency_field()
"""
..todo::
    As this import makes the core depend on the currency extension, we should
    probably integrate this functionality into the core.
"""


""" Abstract base models for essential shop components. """

class UserCustomerBase(AbstractCustomerBase, User):
    """ Abstract base class for customers which can also be Django users. """
    
    class Meta(AbstractCustomerBase.Meta):
        abstract = True

class ProductBase(AbstractPricedItemBase):
    """ Abstract base class for products in the webshop. """

    class Meta(AbstractPricedItemBase.Meta):
        verbose_name = _('product')
        verbose_name_plural = ('products')
        abstract = True
    
    objects = models.Manager()
    in_shop = objects
    """ The `in_shop` property should be a :class:`Manager <django.db.models.Manager>`
        containing all the `Product` objects which should be enabled in the
        shop's frontend.
    """


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
    
    def get_items(self):
        """ Gets all items from the cart with a quantity > 0. """
        
        return self.cartitem_set.filter(quantity__gt=0)
    
    def get_item(self, product):
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
        
    def add_item(self, product, quantity=1):
        """ Adds the specified product in the specified quantity
            to the current shopping Cart. This effectively creates
            a CartItem for the Product-Cart combination or updates
            it when a CartItem already exists.
            
            It returns an _unsaved_ instance of a CartItem, so the
            called is able to determine whether the product was already
            in the shopping cart or not. 
        """
        assert isinstance(quantity, int), 'Quantity not an integer.'
        
        cartitem = self.get_item(product)
        
        # We can do this without querying the actual value from the 
        # database.
        # cartitem.quantity = models.F('quantity') + quantity
        cartitem.quantity += quantity
        
        return cartitem
    
    def get_total_items(self):
        """ 
        Gets the total quantity of products in the shopping cart. 
        
        .. todo::
            Use aggregation here.
        """
        
        quantity = 0
        
        for cartitem in self.get_items():
            quantity += cartitem.quantity
        
        return quantity
    
    def get_price(self, **kwargs):
        """ Wraps the `get_total_price` function. """
        
        return self.get_total_price(**kwargs)
    
    def get_total_price(self, **kwargs):
        """ 
        Gets the total price for all items in the cart. 
        """
        
        logger.debug('Calculating total price for shopping cart.')
        
        # logger.debug(self.get_items()[0].get_total_price())
        
        price = Decimal("0.0")
        
        for cartitem in self.get_items():
            item_price = cartitem.get_total_price(**kwargs)
            logger.debug('Adding price %f for item \'%s\' to total cart price.' % \
                (item_price, cartitem))
            price += item_price
        
        return price

    def get_order_line(self):
        """
        Get a string representation of this `OrderItem` for use in list views.
        """

        return unicode(self.product)


class OrderItemBase(AbstractPricedItemBase, QuantizedItemBase):
    """ 
    Abstract base class for order items. An `OrderItem` should, ideally, copy all
    specific properties from the shopping cart as an order should not change
    at all when the objects they relate to change.
    """

    class Meta(AbstractPricedItemBase.Meta):
        verbose_name = _('order item')
        verbose_name_plural = _('order items')
        abstract = True
        unique_together = ('order', 'product')


    order = models.ForeignKey(ORDER_MODEL)
    """ Order this item belongs to. """

    product = models.ForeignKey(PRODUCT_MODEL)
    """ Product associated with this order item. """

    piece_price = PriceField(verbose_name=_('price per piece'))
    """ Price per piece for the current item. """

    order_line = models.CharField(verbose_name=_('description'),
                                  max_length=255)
    """ Description of this OrderItem as shown on the bill. """

    @classmethod
    def from_cartitem(cls, cartitem, order):
        """
        Create and populate an order item from a shopping cart item.
        The result is *not* automatically saved.

        When the `CartItem` model has extra properties, such as variations,
        these should be copied over to the `OrderItem` in overrides of this
        function as follows::

            class OrderItem(...):
                @classmethod
                def from_cartitem(cls, cartitem, order):
                    orderitem = super(OrderItem, cls).from_cartitem(cartitem, order)

                    orderitem.<someproperty> = cartitem.<someproperty>

                    return orderitem

        """

        orderitem = cls(order=order)
        orderitem.piece_price = cartitem.get_piece_price()
        orderitem.order_line = cartitem.get_order_line()
        orderitem.product = cartitem.product

        return orderitem

    def get_price(self, **kwargs):
        """ Wraps `get_total_price()`. """

        return self.get_total_price(**kwargs)

    def get_total_price(self, **kwargs):
        """ Gets the tatal price for the items in the cart. """

        return self.quantity*self.get_piece_price(**kwargs)

    def get_piece_price(self, **kwargs):
        """ Gets the price per piece for a given quantity of items. """

        return self.piece_price


class OrderStateChangeBase(models.Model):
    """ Abstract base class for logging order state changes. """
    
    class Meta:
        verbose_name = _('order state change')
        verbose_name_plural = _('order state changes')
        abstract = True
    
    order = models.ForeignKey(ORDER_MODEL)
    date = models.DateTimeField(auto_now_add=True, verbose_name=_('date'))
    """ Date at which the state change ocurred. """
    
    state = models.PositiveSmallIntegerField(_('status'), 
                                             choices=ORDER_STATES)
    """ State of the order, represented by a PositveSmallInteger field.
        Available choices can be configured in WEBSHOP_ORDER_STATES. 
    """
    
    notes = models.TextField(blank=True, verbose_name=('notes'))
    """ Any notes manually added to a state change. """


class OrderBase(AbstractPricedItemBase, DatedItemBase):
    """ Abstract base class for orders. """

    class Meta(AbstractPricedItemBase.Meta):
        verbose_name = _('order')
        verbose_name_plural = _('orders')
        abstract = True

    customer = models.ForeignKey(CUSTOMER_MODEL, verbose_name=('customer'))
    """ Customer whom this order belongs to. """
    
    state = models.PositiveSmallIntegerField(_('status'), 
                                             choices=ORDER_STATES,
                                             default=DEFAULT_ORDER_STATE)
    """ State of the order, represented by a PositveSmallInteger field.
        Available choices can be configured in WEBSHOP_ORDER_STATES. 
    """

    def get_items(self):
        """ Get all order items (with a quantity greater than 0). """
        return self.orderitems_set.filter(quantity__gt=0)

    @classmethod
    def from_cart(cls, cart, customer):
        """ 
        Instantiate an order based on the basis of a
        shopping cart, copying all the items. 

        .. todo::
            We should copy any eventual matching fields from the
            cart into the order.
        
        """
        order = cls(customer=customer)

        # Save in order to be able to associate items
        order.save()

        orderitem_class = get_model_from_string(ORDERITEM_MODEL)

        for cartitem in cart.cartitem_set.all():
            orderitem = orderitem_class.from_cartitem(cartitem=cartitem,
                                                      order=order)
            orderitem.save()

            assert orderitem, 'Something went wrong creating an \
                               OrderItem from a CartItem.'


        return order

    def save(self, *args, **kwargs):
        """ 
        
        Make sure we log a state change where applicable. 
        
        .. todo::
            Create a classmethod for creating an OrderState from an order class
            and state.
        
        """
        
        result = super(self, OrderBase).save(*args, **kwargs)

        orderstate_change_class = \
            get_model_from_string(ORDERSTATE_CHANGE_MODEL)

        try:
            latest_statechange = self.orderstatechange_set.all().latest('date')
            
            if latest_statechange.state != self.state:
                # There's a new state change to be made
                
                orderstate_change_class(state=self.state, order=self).save()
            
        except orderstate_change_class.DoesNotExist:
            # No pre-existing state change exists, create new one.

            orderstate_change_class(state=self.state, order=self).save()
        
        return result
        


class PaymentBase(models.Model):
    """ Abstract base class for payments. """
    
    order = models.ForeignKey(ORDER_MODEL)
    """ Order this payment belongs to. """

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')
        abstract = True


