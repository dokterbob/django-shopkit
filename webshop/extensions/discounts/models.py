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
from django.utils.crypto import salted_hmac

from webshop.core.settings import PRODUCT_MODEL
from webshop.core.basemodels import OrderedItemBase

from webshop.extensions.discounts.settings import *


class DiscountBase(models.Model):
    """ Base class for discounts. """
    
    class Meta:
        abstract = True
    
    @classmethod
    def get_valid_discounts(cls, **kwargs):
        """ 
        Get all valid discount objects for a given `kwargs`. Subclasses
        should implement this method.
        """
        
        raise NotImplementedError


class ProductDiscountMixin(object):
    """ Mixin defining discounts based on products. """

    product = models.ForeignKey(PRODUCT_MODEL, db_index=True,
                                verbose_name=_('product'))
    """ Product this discount relates to. """
    
    @classmethod
    def get_valid_discounts(cls, product, *args, **kwargs):
        """ Return valid discounts for a specified product """

        valid = \
            super(ProductDiscountMixin, self).get_valid_discounts(*args, **kwargs)
        
        valid = valid.filter(product=product)
        
        return valid


class ManyProductDiscountMixin(object):
    """ Mixin defining discounts based on products. """

    products = models.ManyToManyField(PRODUCT_MODEL, db_index=True,
                                verbose_name=_('products'))
    """ Products this discount relates to. """
    
    @classmethod
    def get_valid_discounts(cls, product, *args, **kwargs):
        """ Return valid discounts for a specified product """

        valid = \
            super(ProductDiscountMixin, self).get_valid_discounts(*args, **kwargs)
        
        valid = valid.filter(products=product)
        
        return valid


class DateRangeDiscountMixin(object):
    """ Mixin for discount which are only valid within a given date range. """
    
    start_date = models.DateField(verbose_name=_('start date'),
                                  db_index=True)
    end_date = models.DateField(verbose_name=_('end date'),
                                db_index=True)
    
    @classmethod
    def get_valid_discounts(cls, date=None, *args, **kwargs):
        """ Return valid discounts for a specified date, taking the current
            date if no date is specified. """

        valid = \
            super(DateRangeDiscountMixin, self).get_valid_discounts(*args, **kwargs)

        # If no date is set, take today.
        if not date:
            date = datetime.datetime.today()
        
        # Get valid discounts for the current situation
        valid = valid.filter(start_date__gte=date, 
                             end_date__lte=date)
        
        return valid


try:
    from webshop.extensions.settings import CATEGORY_MODEL
    CATEGORIES = True
except ImportError:
    # Apparantly, no category model is defined for this webshop
    CATEGORIES = False
    logger.info('No category model defined, not loading category discounts.')


if CATEGORIES:
    class CategoryDiscountMixin(object):
        """ Mixin defining discounts based on products. """

        category = models.ForeignKey(CATEGORY_MODEL, db_index=True,
                                     verbose_name=_('category'))
        """ Product this discount relates to. """
    
        @classmethod
        def get_valid_discounts(cls, product, *args, **kwargs):
            """ Return valid discounts for a specified product """

            valid = \
                super(CategoryDiscountMixin, self).get_valid_prices(*args, **kwargs)
        
            valid = valid.filter(product=product)
        
            return valid


class CouponDiscountMixin(object):
    """ Discount based on a specified coupon code. """
    
    coupon_code = models.CharField(verbose_name=_('coupon code'),
                                   max_length=COUPON_LENGTH,
                                   help_text=_('If left empty, a code will \
                                                be automatically generated.'))
    """ Code for this coupon, which will be automatically generated upon saving. """
    
    @staticmethod
    def generate_coupon_code():
        """ 
        Generate a coupon code of `COUPON_LENGHT` characters consisting
        of the characters in `COUPON_CHARACTERS`.
        
        .. todo::
            Unittest this function.
        
        """
        rndgen = random.random()
        random.seed()
        
        code = ''
        
        while len(code) < COUPON_LENGTH:
            # Select a random character from COUPON_CHARACTERS and add it to
            # the code.
            code += COUPON_CHARACTERS[random.randint(0, len(COUPON_CHARACTERS)-1)]

        logger.debug('Generated coupon code \'%s\'', code)
        
        return code


    def save(self):
        if not self.coupon_code:
            self.coupon_code = self.generate_coupon_code()
            
        super(CouponDiscountMixin, self).save()
