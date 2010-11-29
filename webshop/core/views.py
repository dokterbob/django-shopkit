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


class CartAddFormMixin(object):
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

        cartform_class = self.get_cart_form_class()
        
        # TODO: check whether a product is available.
        cartform = cartform_class(initial={'product':self.object})        
        
        context = super(CartAddFormMixin, self).get_context_data(**kwargs)
        
        context.update({'cartaddform': cartform})
        
        return context
