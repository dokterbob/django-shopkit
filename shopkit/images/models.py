# Copyright (C) 2010-2011 Mathijs de Bruin <mathijs@mathijsfietst.nl>
#
# This file is part of django-shopkit.
#
# django-shopkit is free software; you can redistribute it and/or modify
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

try:
    from sorl.thumbnail import ImageField    
    logger.debug(u'Sorl-thumbnail found: using it.')

except ImportError:
    ImageField = models.ImageField
    logger.debug(u'Sorl-thumbnail not found. Skipping.')

from shopkit.core.settings import PRODUCT_MODEL
from shopkit.core.basemodels import OrderedInlineItemBase


class ProductImageBase(models.Model):
    """ Base class for image relating to a product. """
    
    class Meta:
        abstract = True
        verbose_name = _('image')
        verbose_name_plural = _('images')

    product = models.ForeignKey(PRODUCT_MODEL)
    image = ImageField(verbose_name=_('image'), 
                       upload_to='product_images')


class OrderedProductImageBase(ProductImageBase, OrderedInlineItemBase):
    """ Base class for explicitly ordere image relating to a product. """
    
    class Meta(ProductImageBase.Meta, OrderedInlineItemBase.Meta):
        abstract = True
        unique_together = ('sort_order', 'product')

    def get_related_ordering(self):
        """ Related objects for generating default ordering. """
        return self.__class__.objects.filter(product=self.product)


class ImagesProductMixin(object):
    """ Mixin representing a product with multiple images
        associated to it.
    """
    
    def get_default_image(self):
        """ By default, this returns the first image according to whatever
            sortorder is used.
        """
        if self.productimage_set.all().count() > 0:
            return self.productimage_set.all()[0]
        else:
            return None
    
    
    

