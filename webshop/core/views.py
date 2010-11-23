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

from webshop.core.util import get_model_from_string
from webshop.core.settings import CART_MODEL
from webshop.core.forms import CartItemAddForm


""" Generic view Mixins for webshop core functionality. """


class CartMixin(object):
    """ View Mixin providing shopping cart functionality. """

    def get_cart(self):
        """ Gets the shopping cart from the context or creates a 
            new one if no shopping cart previously exists.
        """

        cart_class = get_model_from_string(CART_MODEL)
        """ Construct a cart class from the string value in settings. """

        
        cart_pk = self.request.session.get('cart_pk', None)
        
        cart, created = cart_class.objects.get_or_create(pk=cart_pk)
        
        if created:
            logger.debug('Created shopping cart, saving to session.')
            
            self.request.session['cart_pk'] = cart.pk
        else:
            logger.debug('Shopping cart found, pk=%d.' % cart.pk)
        
        return cart
    
    
    def get_context_data(self, **kwargs):
        """ Adds a shopping cart object to the context as `cart`. """
        
        logger.debug('CartMixin')

        context = super(CartMixin, self).get_context_data(**kwargs)
        
        context.update({'cart': self.get_cart()})
        
        return context


class CartFormMixin(object):
    """ Mixin providing a basic form class for adding items to the
        shopping cart. It will be added to the context as `cartaddform`.
    """

    def get_cart_form_class(self):
        """ Simply return the form for adding Items to a Cart. """
        
        return CartItemAddForm
    

    def get_context_data(self, **kwargs):
        """ 
        Add a cart add form under the name `cartaddform` to the 
        context, if and only if an object is available and is a product.
        
        If this is not the case, we should fail silently (perhaps)
        logging a debug message.
        """

        logger.debug('CartFormMixin')
       
        cartform_class = self.get_cart_form_class()
        
        # TODO: check whether a product is available.
        cartform = cartform_class(initial={'product':self.object})        
        
        context = super(CartFormMixin, self).get_context_data(**kwargs)
        
        context.update({'cartaddform': cartform})
        
        return context
