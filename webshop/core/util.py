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

from django.db import models

from webshop.core.settings import CART_MODEL

""" Several util functions for use in core functionality. """


def get_model_from_string(model):
    """ 
    Takes a string in the form of `appname.Model`, (ie.
    `basic_webshop.CartItem`) and returns the model class for it.
    """
    model_class = models.get_model(*model.split('.'))
    
    assert isinstance(model_class, models.base.ModelBase), \
        '%s does not refer to a known Model class.' % model

    return model_class


def get_cart_from_request(request):
    """ Gets the shopping cart from the request or creates a 
        new one if no shopping cart previously exists.
    """

    # Construct a cart class from the string value in settings.
    cart_class = get_model_from_string(CART_MODEL)

    cart_pk = request.session.get('cart_pk', None)
    
    # TODO
    # It should not be necessary to save this cart - this code
    # can be more optimal.
    cart, created = cart_class.objects.get_or_create(pk=cart_pk)
    
    if created:
        logger.debug('Created shopping cart, saving to session.')
        
        request.session['cart_pk'] = cart.pk
    else:
        logger.debug('Shopping cart found, pk=%d.' % cart.pk)
    
    return cart
