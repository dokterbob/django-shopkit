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
from django.utils.translation import ugettext_lazy as _

from webshop.extensions.brands.settings import BRAND_MODEL, BRAND_REQUIRED


class BrandBase(models.Model):
    """ 
    Abstract base class for brands. Use like this::
    
        class Brand(BrandBase, OrderedItemBase, NamedItemBase):
            pass
    
    .. todo::
        Add methods for listing all available products (using the `in_shop`
        manager) for a given brand.
    """
    
    class Meta:
        abstract = True


class BrandedProductMixin(models.Model):
    """ Mixin for product classes with a relation to brand. """
    
    class Meta:
        abstract = True
    
    brand = models.ForeignKey(BRAND_MODEL, verbose_name=_('brand'),
                              null=not BRAND_REQUIRED,
                              blank=not BRAND_REQUIRED)
    """ Brand of the current product. """

