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

from django.utils.translation import ugettext_lazy as _
from django.db import models

from webshop.core.settings import MAX_NAME_LENGTH

""" Generic base models. """


class AbstractCustomerBase(models.Model):
    """ Abstract base class for customers of the shop. """
    
    class Meta:
        verbose_name = _('customer')
        verbose_name_plural = _('customers')
        abstract = True
    
    # def get_first_name(self):
    #     """ This attribute should be accessed as a function as the customer's information 
    #         might originate somewhere else, for example the 
    #         :class:`django.contrib.auth.models.User` model.
    #     """
    #     
    #     raise NotImplementedError


class AbstractPricedItemBase(models.Model):
    """ Abstract base class for items with a price. This only contains
        a `get_price` dummy function yielding a NotImplementedError. An
        actual `price` field is contained in the `PricedItemBase` class.
        
        This is because we might want to get our prices somewhere else, ie.
        using some kind of algorithm, web API or database somewhere.
    """

    class Meta:
        abstract = True

    def get_price(self, **kwargs):
        """ Get price for the current product.
            
            This method _should_ be implemented in a subclass. """

        raise NotImplementedError


class QuantizedItemBase(models.Model):
    """ Abstract base class for items with a quantity field. """
    
    class Meta:
        abstract = True
    
    quantity = models.IntegerField(default=0, verbose_name=_('quantity'))
    """ Number of items of this kind. The default is 0: this is necessary so
    that we can add a certain quantity to a new object without knowing its
    initial value.
    """


class NamedItemBase(models.Model):
    """ Abstract base class for items with a name. """
    
    class Meta:
        abstract = True
    
    name = models.CharField(max_length=MAX_NAME_LENGTH,
                            verbose_name=_('name'))
    """ Name of this item. """

    def __unicode__(self):
        """ Returns the item's name. """
        
        return self.name
