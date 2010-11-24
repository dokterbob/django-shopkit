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

from webshop.extensions.vat.simple import settings

class VATProductBase(ProductBase):
    """ Abstract base class for a simple VAT taxed product where VAT is 
        based on a single configurable percentage. """
    
    class Meta(ProductBase.Meta):
        abstract = True


    def get_taxes(self, **kwargs):
        """ Calculate tax according to a fixed percentage of the price. """

        price = self.get_price(**kwargs)
        
        return settings.VAT_PERCENTAGE * 0.01 * price
