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


class ProductImageBase(models.Model):
    """ Base class for image relating to a product. """
    
    class Meta:
        abstract = True
        verbose_name = _('image')
        verbose_name_plural = _('images')

    product = models.ForeignKey(PRODUCT_MODEL)
    image = models.ImageField(verbose_name=_('image'), 
                              upload_to='product_images')


class OrderedProductImageBase(ProductImageBase, OrderedItemBase):
    """ Base class for explicitly ordere image relating to a product. """
    
    class Meta(ProductImageBase.Meta, OrderedItemBase.Meta):
        abstract = True


    def save(self, **kwargs):
        """ Calculate default ordering for images.
           
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
        
        parent = super(OrderedProductImageBase, self)    
        return parent.save(**kwargs)


class ImagesProductMixin(object):
    """ Mixin representing a product with multiple images
        associated to it.
    """
    
    def get_default_image(self):
        """ By default, this returns the first image according to whatever
            sortorder is used.
        """
        
        return self.productimage_set.all()[0]
    
    
    

