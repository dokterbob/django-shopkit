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
from webshop.core.basemodels import OrderedInlineItemBase


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


class OrderedProductVariationBase(ProductVariationBase, OrderedInlineItemBase):
    """
    Base class for ordered product variations. 
    """
    
    class Meta(ProductVariationBase.Meta, OrderedInlineItemBase.Meta):
        abstract = True
        unique_together = ('sort_order', 'product')

    
    @classmethod
    def get_default_variation(cls):
        """ By default, this returns the first variation according to the
            default sortorder. """
        
        if cls.objects.count():
            return cls.objects.all()[0]
    
    def get_related_ordering(self):
        """ Related objects for generating default ordering. """
        return self.__class__.objects.filter(product=self.product)
