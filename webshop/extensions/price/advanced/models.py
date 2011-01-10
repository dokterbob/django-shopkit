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

import datetime

from django.db import models

from django.utils.translation import ugettext_lazy as _

from webshop.core.util import get_model_from_string
from webshop.core.settings import PRODUCT_MODEL
from webshop.core.basemodels import QuantizedItemBase
from webshop.extensions.price.models import PricedItemBase


class PriceBase(PricedItemBase):
    """ Abstract base class for price models, exposing a method to get the 
        cheapest price under given conditions.
        
        Be sure to add the proper `unique_together` contraints to subclasses
        implementing an actual price model. 
    """
    
    class Meta(PricedItemBase.Meta):
        abstract = True
    
    @staticmethod
    def _get_minimal_price(qs):
        """ Get the minimal price within the given QuerySet. """
        
        assert qs.count(), \
            'FIXME: No prices found. This will raise an exception that should be called.'

        return qs.aggregate(models.Min('price'))['price__min']
    
    
    @classmethod
    def get_cheapest(cls, **kwargs):
        """ Get the cheapest available price under
            given conditions. """
        
        valid = cls.get_valid_prices(**kwargs)
        
        return cls._get_minimal_price(valid)
    
    
    @classmethod
    def get_valid_prices(cls, **kwargs):
        """ 
        Get valid prices (as a QuerySet), given certain constraints. By
        default, this returns all prices available. Where applicable,
        subclasses might filter this result by:
            
            * Product
            * Date
            * Quantity
        """

        return cls.objects.all()


    def __unicode__(self):
        """ Return the formatted value of the price. """
        
        # TODO: Do price formatting in a generic manner.
        return u'%2.2f' % self.get_price()


class ProductPriceMixin(models.Model):
    """ Represents prices available for a specific product product. """
    

    class Meta:
        abstract = True

    product = models.ForeignKey(PRODUCT_MODEL, db_index=True,
                                verbose_name=_('product'))
    """ Product this price relates to. """
    
    @classmethod
    def get_valid_prices(cls, product, *args, **kwargs):
        """ Return valid prices for a specified product """

        valid = \
            super(ProductPriceBase, self).get_valid_prices(*args, **kwargs)
        
        valid = valid.filter(product=product)
        
        return valid


class DateRangedPriceMixin(models.Model):
    """ Base class for a price that is only valid within a given date range. 
    """

    class Meta:
        abstract = True
        # unique_together = ('product', 'start_date', 'end_date')

    start_date = models.DateField(verbose_name=_('start date'),
                                  db_index=True)
    end_date = models.DateField(verbose_name=_('end date'),
                                db_index=True)
    
    @classmethod
    def get_valid_prices(cls, date=None, *args, **kwargs):
        """ Return valid prices for a specified date, taking the current
            date if no date is specified. """

        valid = \
            super(DateRangedPriceBase, self).get_valid_prices(*args, **kwargs)

        # If no date is set, take today.
        if not date:
            date = datetime.datetime.today()
        
        # First get valid prices for the current situation
        valid = valid.filter(product=product, 
                           start_date__gte=date, 
                           end_date__lte=date)
        
        return valid


class QuantifiedPriceMixin(QuantizedItemBase):
    """ Base class for a price that is only valid above a certain quantity.
    """

    class Meta:
        abstract = True
        # unique_together = ('product', 'quantity')

    @classmethod
    def get_valid_prices(cls, quantity=1, *args, **kwargs):
        """ Get valid prices for a given quantity of items. If no
            quantity is given, 1 is assumed. 
        """
        
        valid = \
            super(QuantifiedPriceBase, self).get_valid_prices(*args, **kwargs)
                
        # First get valid prices for the current situation
        valid = valid.filter(quantity__gte=quantity)
        
        return valid


# class PricedItemBase(models.Model):
#     """ Abstract base class for an advanced priced product. 
#         This base class allows for more complex pricing of articles, it 
#         enables features like:
#         
#         * Returning and storing different prices depending on a date range.
#         * Returning and storing different prices depending on the quantity.
#     """
#     
#     
#     class Meta:
#         abstract = True
#     
#     def get_price(self, **kwargs):
#         """ Get the cheapest available price, based
#             upon WEBSHOP_PRICE_MODEL. """
#         
#         cheapest = self.__class__.get_cheapest(**kwargs)
#         
#         return cheapest.get_price(**kwargs)
# 
# 
