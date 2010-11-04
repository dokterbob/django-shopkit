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

from django.db import models

class ProductBase(models.Model):
    """ Abstract base model for products. """

    class Meta:
        abstract = True

    def get_price(self, *args, **kwargs):
        """ Get price for the current product.
            
            This method _should_ be implemented in a subclass. """

        raise Exception('Not implemented')

class CartBase(models.Model):
    """ Abstract base class for shopping carts. """

    class Meta:
        abstract = True

class OrderBase(models.Model):
    """ Abstract base class for orders. """

    class Meta:
        abstract = True

class PaymentBase(models.Model):
    """ Abstract base class for payments. """

    class Meta:
        abstract = True

