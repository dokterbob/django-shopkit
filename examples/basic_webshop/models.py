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


from webshop.core.models import ProductBase, CartBase, CartItemBase, \
                                OrderBase, OrderItemBase, UserCustomerBase
                                
from webshop.core.basemodels import NamedItemBase

from webshop.extensions.category.simple.models import CategoryBase, \
                                                      CategorizedItemBase
from webshop.extensions.price.simple.models import PricedItemBase


class Customer(UserCustomerBase):
    """ Basic webshop customer. """
    pass

class Product(ProductBase, CategorizedItemBase, PricedItemBase, NamedItemBase):
    """ Basic product model. 
    
    >>> c = Category(name='Fruit', slug='fruit')
    >>> c.save()
    >>> p = Product(category=c, name='Banana', slug='banana', price="15.00")
    >>> p.description = 'A nice piece of fruit for the whole family to enjoy.'
    >>> p.save()
    >>> c.product_set.all()
    [<Product: Banana>]
    
    """
    
    class Meta:
        unique_together = ('category', 'slug')
   
    slug = models.SlugField()
    description = models.TextField(blank=False)

    @models.permalink
    def get_absolute_url(self):
        return 'product_detail', None, \
            {'category_slug': self.category.slug,
             'slug': self.slug}

class Cart(CartBase):
    """ Basic shopping cart model. """
    
    pass

class CartItem(CartItemBase):
    """ Item in a shopping cart. """
    
    pass

class Order(OrderBase):
    """ Basic order model. """
    
    pass

class OrderItem(OrderItemBase):
    """ Item in an order. """
    
    pass

class Category(CategoryBase, NamedItemBase):
    """ Basic category model. """
    
    slug = models.SlugField(unique=True)
    
    def get_products(self):
        """ Get all active products for the current category. """
        return Product.in_shop.filter(category=self)
    
    @models.permalink
    def get_absolute_url(self):
        return 'category_detail', None, \
            {'slug': self.slug}

