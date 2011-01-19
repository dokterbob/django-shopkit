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
from django.utils.translation import ugettext_lazy as _

from webshop.core.settings import PRODUCT_MODEL
from webshop.core.basemodels import OrderedItemBase


class ProductVariationBase(models.Model):
    """ Base class for variations of a product. """
    
    class Meta:
        verbose_name = _('product variation')
        verbose_name_plural = _('product variations')
        abstract = True
    
    @classmethod
    def get_default_variation(cls):
        """ Return the default variation selected for this product.
            As there is no inherent way to order these, this function
            should be overridden in classes actually implementing the
            variation model.
            
            This might, for example, be overriden by taking the first product
            in the list or by some function selecting a specific variation as
            default.
        """
        
        raise NotImplemented
    
    product = models.ForeignKey(PRODUCT_MODEL)
    """ Product this variation is linked to. """


class OrderedProductVariationBase(ProductVariationBase, OrderedItemBase):
    """
    Base class for ordered product variations. 
    
    .. todo::
        Get rid of uniqueness constraint in OrderItemBase -- either by
        removing it from the base model or by not inheriting from it.

    """
    
    class Meta(ProductVariationBase.Meta, OrderedItemBase.Meta):
        abstract = True
    
    @classmethod
    def get_default_variation(cls):
        """ By default, this returns the first variation according to the
            default sortorder. """
        
        return self.__class__.objects.all()[0]
    
    
    def save(self, **kwargs):
        """ Calculate default ordering for products.
           
            This code is inspired by from `django-inline-ordering <https://github.com/centralniak/django-inline-ordering/blob/master/inline_ordering/models.py>`_.
            
        """
        
        if not self.sort_order:
            related_variations = \
                self.__class__.objects.filter(product=self.product)
            
            max_ordering_query = \
                related_variations.aggregate(models.Max('sort_order'))
            
            max_ordering = max_ordering_query['sort_order__max']
            
            if max_ordering:
                self.sort_order = max_ordering + 10
            else:
                self.sort_order = 10
            
            logger.debug('Generated sort_order %d for object %s',
                         self.sort_order, self)
        
        parent = super(OrderedProductVariationBase, self)    
        return parent.save(**kwargs)


