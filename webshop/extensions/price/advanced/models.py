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

from webshop.core.settings import PRODUCT_MODEL
from webshop.extensions.price.models import PricedItemBase

from webshop.extensions.price.advanced.settings import *


class PriceBase(PricedItemBase):
    """ Abstract base class for price models, exposing a method to get the 
        cheapest price under given conditions. 
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
    def get_cheapest(cls, product, **kwargs):
        """ Get the cheapest available price for the current product under
            given conditions. """
        
        valid = cls.get_valid(product, **kwargs)
        
        return cls._get_minimal_price(valid)
    
    @classmethod
    def get_valid(cls, product, **kwargs):
        """ Get valid prices under the given conditions. This should be
            overriden for subclasses actually implementing some features.
        """

        raise NotImplementedError


class DateRangedPriceBase(PriceBase):
    """ Base class for a price that is only valid within a given date range. """

    class Meta(PriceBase.Meta):
        abstract = True
        unique_together = ('product', 'start_date', 'end_date')

    product = models.ForeignKey(PRODUCT_MODEL, db_index=True,
                                verbose_name=_('product'))
    start_date = models.DateField(verbose_name=_('start date'), db_index=True)
    end_date = models.DateField(verbose_name=_('end date'), db_index=True)
    
    @classmethod
    def get_valid(cls, product, date=None, *args, **kwargs):
        """ Return valid prices for a specified date, taking the current
            date if no date is specified. """

        # If no date is set, take today.
        if not date:
            date = datetime.datetime.today()
        
        # First get valid prices for the current situation
        valid = cls.filter(product=product, 
                           start_date__gte=date, 
                           end_date__lte=date)
        
        return valid


class QuantifiedPriceBase(PriceBase):
    """ Base class for a price that is only valid above a certain quantity. """

    class Meta(PriceBase.Meta):
        abstract = True
        unique_together = ('product', 'quantity')

    product = models.ForeignKey(PRODUCT_MODEL, db_index=True,
                                verbose_name=_('product'))
    quantity = models.IntegerField(default=1, db_index=True,
                                   verbose_name=('quantity'))

    @classmethod
    def get_valid(cls, product, quantity=1, *args, **kwargs):
        """ Get valid prices for a given quantity of items. If no
            quantity is given, 1 is assumed. 
        """
                
        # First get valid prices for the current situation
        valid = cls.filter(product=product, 
                           quantity__gte=quantity)
        
        return valid


class PricedProductBase(models.Model):
    """ Abstract base class for an advanced priced product. 
        This base class allows for more complex pricing of articles, it 
        enables features like:
        
        * Returning and storing different prices depending on a date range.
        * Returning and storing different prices depending on the quantity.
    """
    
    class Meta:
        abstract = True
    
    def get_price(self, **kwargs):
        """ Iterate over the models in `WEBSHOP_PRICE_MODELS` in order
            to find the lowest possible price under the conditions specified
            in the arguments.
        """
        
        # Iterate over the specified price models 
        # TODO: We might consider some kind of registration for price
        # models instead of using something in settings.py
        
        # TODO2: Caching might be nice.

        cheapest = None        
        for model_name in PRICE_MODELS:
            model = models.get_model(*model_name.split('.'))

            # Execute the get_cheapest class model for efficient price
            # finding.
            this_cheapest = model.get_cheapest(**kwargs)
            
            # Compare to the cheapest price so far and if it's cheaper,
            # use it.
            if cheapest and this_cheapest and \
                    this_cheapest.get_price(**kwargs) < cheapest.get_price(**kwargs):
                
                cheapest = this_cheapest
        
        return cheapest.get_price(**kwargs)
