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

