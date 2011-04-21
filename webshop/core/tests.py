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

from django.conf import settings

from webshop.core.utils import get_model_from_string


class CoreTestMixin(object):
    """ Base class for testing core webshop functionality. This class should
        not directly be used, rather it should be subclassed similar to the
        way that included model base classes should be subclassed.
    """
    
    def setUp(self):
        """ 
        This function gets the model classes from `settings.py` and
        makes them available as `self.cusomter_class`, `self.product_class` 
        etcetera.
        """
        super(CoreTestMixin, self).setUp()
        
        self.customer_class = \
            get_model_from_string(settings.WEBSHOP_CUSTOMER_MODEL)
        
        self.product_class = \
            get_model_from_string(settings.WEBSHOP_PRODUCT_MODEL)
        
        self.cart_class = \
            get_model_from_string(settings.WEBSHOP_CART_MODEL)

        self.cartitem_class = \
            get_model_from_string(settings.WEBSHOP_CARTITEM_MODEL)

        self.order_class = \
            get_model_from_string(settings.WEBSHOP_ORDER_MODEL)

        self.orderitem_class = \
            get_model_from_string(settings.WEBSHOP_ORDERITEM_MODEL)
    
    def make_test_product(self):
        """ 
        Abstract function for creating a test product. As the actual
        properties of Products depend on the classes actually implementing
        it, this function must be overridden in subclasses.
        """
        raise NotImplementedError

    def test_basic_product(self):
        """ Test if we can create and save a simple product. """
        
        p = self.make_test_product()
        p.save()
        
        self.assert_(p.pk)
        
    def test_cartitem_from_product(self):
        """ Create a `CartItem` from a `Product`. """
        pass
    
    def test_orderitem_from_cartitem(self):
        """ Create an `OrderItem` from a `CartItem`. """
        pass
    
    def test_create_usercustomer(self):
        """ Create a `UserCustomer`. """
        pass
    
    def test_cart(self):
        """ 
        Create a shopping cart with several products, quantities and
        prices.
        """
        pass
    
    def test_order(self):
        """
        Create an order on the basis of a shopping cart and a customer
        object.
        """
        pass
    
    def test_orderstate_change_tracking(self):
        """
        Change the state of an order, see if the state change gets logged.
        """
        pass

