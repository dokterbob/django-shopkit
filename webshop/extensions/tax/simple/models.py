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

from webshop.core.models import ProductBase

from webshop.extensions.tax.simple import settings

class TaxedProductBase(ProductBase):
    """ Abstract base class for a simple taxed product where tax is 
        based on a configurable percentage. """
    
    class Meta(ProductBase.Meta):
        abstract = True


    def get_taxes(self, *args, **kwargs):
        """ Calculate tax according to a fixed percentage of the price. """

        price = self.get_price(*args, **kwargs)
        
        return settings.TAX_PERCENTAGE * price
