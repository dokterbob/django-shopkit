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

from decimal import Decimal

from django.contrib.auth.models import User

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.db import models

from shopkit.core.settings import PRODUCT_MODEL, CART_MODEL, \
                                  CARTITEM_MODEL, ORDER_MODEL, \
                                  ORDERITEM_MODEL, CUSTOMER_MODEL, \
                                  ORDERSTATE_CHANGE_MODEL, ORDER_STATES, \
                                  DEFAULT_ORDER_STATE
from shopkit.core import signals
from shopkit.core.basemodels import AbstractPricedItemBase, DatedItemBase, \
                                    QuantizedItemBase, AbstractCustomerBase

from shopkit.core.utils import get_model_from_string

from shopkit.core.exceptions import AlreadyConfirmedException

# Get the currently configured currency field, whatever it is
from shopkit.currency.utils import get_currency_field
PriceField = get_currency_field()
"""
..todo::
    As this import makes the core depend on the currency extension, we should
    probably integrate this functionality into the core.
"""

from shopkit.core.listeners import *


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

        piece_price = self.get_piece_price(**kwargs)
        assert isinstance(piece_price, Decimal)

        price = self.quantity*piece_price

        return price

    def get_piece_price(self, **kwargs):
        """ Gets the price per piece for a given quantity of items. """

        return self.product.get_price(quantity=self.quantity, **kwargs)

    def get_order_line(self):
        """
        Natural (unicode) representation of this cart item in an order
        overview.
        """
        return unicode(self)

    def get_parent(self):
        """
        Get the relevant Cart. Used to have a generic API for Carts 
        and Orders.
        """
        return self.cart

class CartBase(AbstractPricedItemBase):
    """ Abstract base class for shopping carts. """

    class Meta(AbstractPricedItemBase.Meta):
        verbose_name = _('cart')
        verbose_name_plural = _('carts')
        abstract = True

    customer = models.ForeignKey(CUSTOMER_MODEL, verbose_name=('customer'), null=True)
    """ Customer who owns this cart, if any. """

    @classmethod
    def from_request(cls, request):
        """
        Get an existing `Cart` object from the session or return a blank one.

        :returns: `Cart` object corresponding with this request
        """
        cart_pk = request.session.get('cart_pk', None)

        if cart_pk:
            logger.debug('Found shopping cart PK in session.')

            try:
                cart = cls.objects.get(pk=cart_pk)
            except cls.DoesNotExist:
                logger.warning(u'Shopping cart not found for pk %d.', cart_pk)

                cart = cls()
        else:
            logger.debug('No shopping cart found. Creating new instance.')
            cart = cls()

        if not cart.customer and request.user.is_authenticated():
            try:
                customer = request.user.customer

                logger.debug(u'Setting customer for cart to %s', customer)

                cart.customer = customer
            except ObjectDoesNotExist:
                logger.info(u'User %s logged in but no customer object '+
                            u'found. This user will not be able to buy '+
                            u'products.', request.user)

        return cart

    def to_request(self, request):
        """
        Store a reference to the current `Cart` object in the session.
        """
        assert self.pk, 'Cart object not saved'

        logger.debug('Storing shopping cart with pk %d in session.' % self.pk)
        request.session['cart_pk'] = self.pk

    def get_items(self):
        """ Gets items from the cart with a quantity > 0. """

        return self.cartitem_set.filter(quantity__gt=0)

    def get_item(self, product, create=True, **kwargs):
        """ Either instantiates and returns a CartItem for the
            Cart-Product combination or fetches it from the
            database. The creation is lazy: the resulting CartItem
            is not automatically saved.

            :param create:
                Whether or not to create a new object if no object was found.

            :param kwargs:
                If `kwargs` are specified, these signify filters or instantiation
                parameters for getting or creating the item.
        """

        # It makes more sense to execute this code on a higher level
        # instead of everytime a cart item is requested.
        cartitem_class = get_model_from_string(CARTITEM_MODEL)

        # Note that we won't use 'get_or_create' here as it automatically
        # saves the object.
        try:
            cartitem = cartitem_class.objects.get(cart=self,
                                                  product=product,
                                                  **kwargs)

            logger.debug(u'Found existing cart item for product \'%s\'' \
                            % product)

        except cartitem_class.DoesNotExist:
            if create:
                logger.debug(u'Product \'%s\' not already in Cart, creating item.' \
                                % product)

                cartitem = cartitem_class(cart=self,
                                          product=product,
                                          **kwargs)
            else:
                return None

        return cartitem

    def add_item(self, product, quantity=1, **kwargs):
        """ Adds the specified product in the specified quantity
            to the current shopping Cart. This effectively creates
            a CartItem for the Product-Cart combination or updates
            it when a CartItem already exists.

            When `kwargs` are specified, these are passed along to
            `get_item` and signify properties of the `CartItem`.

            :returns: added `CartItem`
        """
        # assert isinstance(quantity, int), 'Quantity not an integer.'

        cartitem = self.get_item(product, **kwargs)

        assert cartitem.product == product
        assert cartitem.product.pk, 'No pk for product, please save first'

        # We can do this without querying the actual value from the
        # database.
        # cartitem.quantity = models.F('quantity') + quantity
        cartitem.quantity += quantity

        cartitem.save()
        assert cartitem.pk

        return cartitem

    def remove_item(self, product, **kwargs):
        """
        Remove item from cart.

        :returns:
            True if the item was deleted succesfully, False if the item
            could not be found.
        """

        cartitem = self.get_item(product, create=False, **kwargs)

        if cartitem:
            cartitem.delete()
            return True

        return False

    def get_total_items(self):
        """
        Gets the total quantity of products in the shopping cart.

        .. todo::
            Use aggregation here.
        """

        quantity = 0

        for cartitem in self.get_items():
            quantity += cartitem.quantity

        # assert isinstance(quantity, int)
        return quantity

    def get_price(self, **kwargs):
        """ Wraps the `get_total_price` function. """

        return self.get_total_price(**kwargs)

    def get_total_price(self, **kwargs):
        """
        Gets the total price for all items in the cart.
        """

        logger.debug(u'Calculating total price for shopping cart.')

        # logger.debug(self.get_items()[0].get_total_price())

        price = Decimal("0.0")

        for cartitem in self.get_items():
            item_price = cartitem.get_total_price(**kwargs)
            logger.debug(u'Adding price %f for item \'%s\' to total cart price.' % \
                (item_price, cartitem))
            assert isinstance(item_price, Decimal)

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

    product = models.ForeignKey(PRODUCT_MODEL, on_delete=models.PROTECT)
    """ Product associated with this order item. """

    piece_price = PriceField(verbose_name=_('price per piece'),
                             default=Decimal('0.00'))
    """ Price per piece for the current item. """

    order_line = models.CharField(verbose_name=_('description'),
                                  max_length=255)
    """ Description of this OrderItem as shown on the bill. """

    def __unicode__(self):
        """ A natural representation for a cart item is the product. """

        return unicode(self.product)

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
        orderitem.quantity = cartitem.quantity

        return orderitem

    def get_price(self, **kwargs):
        """ Wraps `get_total_price()`. """

        return self.get_total_price(**kwargs)

    def get_total_price(self, **kwargs):
        """ Gets the tatal price for the items in the cart. """

        piece_price = self.get_piece_price(**kwargs)
        assert isinstance(piece_price, Decimal)

        price = self.quantity*piece_price

        return price

    def get_piece_price(self, **kwargs):
        """ Gets the price per piece for a given quantity of items. """

        return self.piece_price

    def confirm(self):
        """
        Register confirmation of the current `OrderItem`. This can be
        overridden in subclasses to perform functionality such as stock
        keeping or discount usage administration. By default it merely
        emits a debug message.

        When overriding, be sure to call the superclass.
        """
        logger.debug(u'Registering order item confirmation for %s', self)

    def get_parent(self):
        """
        Get the relevant Order. Used to have a generic API for Carts 
        and Orders.
        """
        return self.order


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
        Available choices can be configured in SHOPKIT_ORDER_STATES.
    """

    message = models.CharField(_('message'),
                               blank=True, null=True, max_length=255)

    @classmethod
    def get_latest(cls, order):
        """
        Get the latest state change for a particular order, or `None` if no
        `StateChange` is available.
        """
        try:
            return cls.objects.filter(order=order).order_by('-pk').latest('date')
        except cls.DoesNotExist:
            logger.debug(u'Latest state change for %s not found', order)
            return None

    def __unicode__(self):
        return _(u'%(order)s on %(date)s to %(state)s: %(message)s') % \
            {'order': self.order,
             'date': self.date,
             'state': self.state,
             'message': self.message
            }


class OrderBase(AbstractPricedItemBase, DatedItemBase):
    """ Abstract base class for orders. """

    class Meta(AbstractPricedItemBase.Meta):
        verbose_name = _('order')
        verbose_name_plural = _('orders')
        abstract = True

    cart = models.ForeignKey(CART_MODEL, verbose_name=_('cart'),
                             null=True, on_delete=models.SET_NULL)
    """ Shopping cart this order was created from. """

    customer = models.ForeignKey(CUSTOMER_MODEL, verbose_name=('customer'),
                                 on_delete=models.PROTECT)
    """ Customer whom this order belongs to. """

    state = models.PositiveSmallIntegerField(_('status'),
                                             choices=ORDER_STATES,
                                             default=DEFAULT_ORDER_STATE)
    """ State of the order, represented by a PositveSmallInteger field.
        Available choices can be configured in SHOPKIT_ORDER_STATES.
    """

    confirmed = models.BooleanField(_('confirmed'),
                                    default=False,
                                    editable=False)
    """
    Whether or not the order has been confirmed by calling the
    `confirm()` method. This field exists in order to prevent potentially
    disastrous double registration of confirmation, where an `Order`'s stock
    would be lowered twice etcetera.
    """

    def get_items(self):
        """ Get all order items (with a quantity greater than 0). """
        return self.orderitem_set.filter(quantity__gt=0)

    def get_total_items(self):
        """
        Gets the total quantity of products in the shopping cart.

        .. todo::
            Use aggregation here.
        """

        quantity = 0

        for orderitem in self.get_items():
            # assert isinstance(orderitem.quantity, int)
            quantity += orderitem.quantity

        return quantity

    @classmethod
    def from_cart(cls, cart):
        """
        Instantiate an order based on the basis of a
        shopping cart, copying all the items.
        """

        assert cart.customer

        order = cls(customer=cart.customer, cart=cart)

        # Save in order to be able to associate items
        order.save()

        orderitem_class = get_model_from_string(ORDERITEM_MODEL)

        for cartitem in cart.cartitem_set.all():
            orderitem = orderitem_class.from_cartitem(cartitem=cartitem,
                                                      order=order)
            orderitem.save()

            assert orderitem, 'Something went wrong creating an \
                               OrderItem from a CartItem.'
            assert orderitem.pk

        assert len(cart.get_items()) == len(order.get_items())

        return order

    def _update_state(self, message=None):
        """
        Update the order state, optionaly attach a message to the state
        change. When no message has been given and the order state is the
        same as the previous order state, no action is performed.
        """

        assert self.pk, 'Cannot update state for unsaved order.'

        orderstate_change_class = \
            get_model_from_string(ORDERSTATE_CHANGE_MODEL)

        latest_statechange = orderstate_change_class.get_latest(order=self)

        if latest_statechange:
            latest_state = latest_statechange.state
        else:
            latest_state = None

        logger.debug(u'Considering state change: %s %s %s',
                     self,
                     latest_state,
                     self.state)
        if latest_state is None or latest_state != self.state or message:
            state_change = orderstate_change_class(state=self.state,
                                                   order=self,
                                                   message=message)
            state_change.save()

            # There's a new state change to be made
            logger.debug(u'Saved state change from %s to %s for %s with message \'%s\'',
                         latest_state,
                         self.state,
                         self,
                         message)

            # Send order_state_change signal
            results = signals.order_state_change.send_robust(
                                            sender=self,
                                            old_state=latest_state,
                                            new_state=self.state,
                                            state_change=state_change)

            # Re-raise exceptions in listeners
            for (receiver, response) in results:
                if isinstance(response, Exception):
                    raise response

        else:
            logger.debug(u'Same state %s for %s, not saving change.',
                         self.state, self)

    def save(self, *args, **kwargs):
        """
        Make sure we log a state change where applicable.
        """

        result = super(OrderBase, self).save(*args, **kwargs)

        self._update_state()

        return result

    def prepare_confirm(self):
        """
        Run necessary checks in order to confirm whether an order can be
        safely confirmed. By default this method only checks whether or not
        the order has already been confirmed, but could be potentially
        overridden by methods checking the item's stock etcetera.

        :raises: AlreadyConfirmedException
        """

        # Check whether this order is already confirmed, in which case
        # we should raise an exception.
        if self.confirmed:
            raise AlreadyConfirmedException(self)

    def confirm(self):
        """
        Method which performs actions to be taken upon order confirmation.

        By default, this method writes a log message and calls the
        `register_confirmation` method on all order items. It also deletes
        to shopping cart this order was created from.

        Subclasses can use this to perform actions such as updating the
        stock or registering the use of a discount. When overriding, make sure
        this method calls its supermethods.

        When subclassing this method, please make sure you implement proper
        safety checks in the overrides of the `prepare_confirm()` method as
        this method should *not* raise errors under normal circumstances as
        this could lead to potential data/state inconsistencies.

        In general, it makes sense to connect this method to a change in order
        state such that it is called automatically. For example:

        ..todo::
            Write a code example here.

        """
        assert not self.confirmed, \
            'Order already confirmed, you should run prepare_confirm() first!'

        logger.debug(u'Registering order confirmation for %s', self)

        # Delete shopping cart
        if self.cart:
            self.cart.delete()

        # Confirm registration before doing anything else: when an Exception
        # *does* occur in the process, we do not want to risk being able
        # to call `confirm()` again.
        self.confirmed = True
        
        # Make sure the cart is reset in order to preserve referential
        # integrity
        self.cart = None
        self.save()

        for item in self.get_items():
            item.confirm()

    def get_price(self, **kwargs):
        """ Wraps the `get_total_price` function. """

        return self.get_total_price(**kwargs)

    def get_total_price(self, **kwargs):
        """
        Gets the total price for all items in the order.
        """

        logger.debug(u'Calculating total price for order.')

        # logger.debug(self.get_items()[0].get_total_price())

        price = Decimal("0.0")

        for orderitem in self.get_items():
            item_price = orderitem.get_total_price(**kwargs)
            logger.debug(u'Adding price %f for item \'%s\' to total price.' % \
                (item_price, orderitem))
            assert isinstance(item_price, Decimal)
            price += item_price

        return price

    def __unicode__(self):
        """ Textual representation of order. """

        return _(u"%(pk)d by %(customer)s on %(date)s") % \
            {'pk': self.pk,
             'customer': self.customer,
             'date': self.date_added.date()
            }

class AddressBase(models.Model):
    """
    Base class for address models.

    This base class should be used when defining addresses for customers.
    """

    class Meta:
        abstract = True
        verbose_name = _('address')
        verbose_name_plural = _('addresses')

    addressee = models.CharField(_('addressee'), max_length=255)
    """ Addressee for the current address. """

    def __unicode__(self):
        """ Return the addressee property. """
        return self.addressee


class CustomerAddressBase(models.Model):
    """
    Base class for addresses with a relation to a customer, for which the
    `addressee` field is automatically set when saving.
    """

    class Meta(AddressBase.Meta):
        abstract = True

    addressee = models.CharField(_('addressee'), max_length=255, blank=True,
                                 help_text=_('Automatically set to the name of the customer when left empty.'))
    customer = models.ForeignKey(CUSTOMER_MODEL, editable=False)

    def save(self, **kwargs):
        """
        Default the addressee to the full name of the user if none has
        been specified explicitly.
        """

        if not self.addressee:
            assert self.customer

            self.addressee = self.customer.get_full_name()

        super(CustomerAddressBase, self).save(**kwargs)

    def __unicode__(self):
        """ Return the addressee property. """
        return self.addressee


class PaymentBase(models.Model):
    """ Abstract base class for payments. """

    order = models.ForeignKey(ORDER_MODEL)
    """ Order this payment belongs to. """

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')
        abstract = True


