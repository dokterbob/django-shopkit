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

from webshop.core.basemodels import AbstractPricedItemBase

from webshop.extensions.vat.simple.settings import VAT_PERCENTAGE, VAT_DEFAULT_DISPLAY


class VATItemBase(AbstractPricedItemBase):
    """ This item extends any priced item (subclasses of :class:`AbstractPricedItemBase`) 
        with functions that yield the prices with and without VAT. In doing this,
        it might be imported in what order the base classes for the VAT'ed item are
        listed. Feedback about this is welcomed.
        
        TODO: Write tests for this piece of code.
    """

    def get_vat(**kwargs):
        """ Gets the amount of VAT for the current item. """
        
        kwargs.update({'with_vat': False})        
        return self.get_price(**kwargs) * 0.01 * VAT_PERCENTAGE

    def get_price(with_vat=VAT_DEFAULT_DISPLAY, **kwargs):
        """ If `with_vat=False`, simply returns the original price. Otherwise
            it takes the result of `get_vat()` and adds it to the original price. """
            
        # Get the price without VAT
        without_kwargs = kwargs.copy()
        without_kwargs.update({'with_vat': False})
        price_without = super(VATItemBase, self).get_price(**without_kwargs)
        
        if with_vat:
            return price_without + self.get_vat(**kwargs)
        
        return price_without
    
    def get_price_with_vat(**kwargs):
        """ Gets the price including VAT. This is a wrapper function around
            get_price as to allow for specific prices to be queried from within
            templates. """
        
        kwargs.update({'with_vat': True})
        
        return self.get_price(**kwargs)
    
    def get_price_without_vat(**kwargs):
        """ Gets the price excluding VAT. This is a wrapper function around
            get_price as to allow for specific prices to be queried from within
            templates. """
        
        kwargs.update({'with_vat': False})
        
        return self.get_price(**kwargs)
