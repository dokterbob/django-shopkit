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

from django.test import TestCase

from webshop.core.util import get_model_from_string


class CoreTestBase(TestCase):
    """ Base class for testing core webshop functionality. This class should
        not directly be used, rather it should be subclassed similar to the
        way that included model base classes should be subclassed.
    """
    
    def setUp(self):
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
        
