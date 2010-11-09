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

from webshop.core.models import ProductBase, CartBase, OrderBase
from webshop.core.basemodels import NamedItemBase

from webshop.extensions.category.simple.models import CategoryBase, \
                                                      CategorizedProductBase

from django.db import models


class Product(CategorizedProductBase, NamedItemBase):
    """ Basic product model. """
    
    class Meta(CategorizedProductBase.Meta):
        unique_together = ('category', 'slug')
        
    slug = models.SlugField()

class Cart(CartBase):
    """ Basic shopping cart model. """
    
    pass

class Order(OrderBase):
    """ Basic order model. """
    
    pass

class Category(CategoryBase, NamedItemBase):
    """ Basic category model. """
    
    slug = models.SlugField(unique=True)

