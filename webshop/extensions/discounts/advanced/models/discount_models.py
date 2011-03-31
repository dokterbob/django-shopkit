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

"""
Model base and mixin classes for building discount model and logic.

.. todo::
    Provide a listing/overview of the types of DiscountMixin's available,
    how they should be used and... whether they have been tested or not.
"""

import logging
logger = logging.getLogger(__name__)

from decimal import Decimal

from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from webshop.extensions.discounts.settings import \
    COUPON_LENGTH, COUPON_CHARACTERS

from datetime import datetime

from webshop.core.settings import PRODUCT_MODEL
from webshop.core.utils.fields import PercentageField

# Get the currently configured currency field, whatever it is
from webshop.extensions.currency.utils import get_currency_field
PriceField = get_currency_field()


class DiscountBase(models.Model):
    """ Base class for discounts. """

    class Meta:
        abstract = True

    @classmethod
    def get_valid_discounts(cls, **kwargs):
        """
        Get all valid discount objects for a given `kwargs`. By default,
        all discounts are valid.
        """

        return cls.objects.none()

    @classmethod
    def get_all_discounts(cls):
        """ Get all discounts, whether valid or not. """

        return cls.objects.all()

    def is_valid(self, **kwargs):
        """
        Check to see whether an individual discount is valid under the
        given circumstances.
        """

        valid = self.get_valid_discounts(**kwargs)

        assert self.pk, \
        "This discount has not yet been saved, which is required in order \
         to determine it's validity (for now)."

        valid.filter(pk=self.pk)

        return valid.exists()

    def get_discount(self, **kwargs):
        """
        Get the total amount of discount produced by this `Discount`. This
        method should be implemented by subclasses of `:class:DiscountBase`.
        """
        return Decimal('0.00')

    def __unicode__(self):
        """
        Natural representation of discount. For now, just use the pk.
        """
        return self.pk

class OrderDiscountAmountMixin(models.Model):
    """
    Mixin for absolute amount discounts which act on the total price
    for an order.
    """

    class Meta:
        abstract = True

    order_amount = PriceField(verbose_name=_('order discount amount'),
                              null=True, blank=True)
    """ Absolute discount on the total of an order. """

    @classmethod
    def get_valid_discounts(cls, **kwargs):
        """
        We want to be able to discriminate between discounts valid for
        the whole order and those valid for order items.

        :param order_discounts: When `True`, only items for which
                               `order_amount` has been specified are valid.
                               When `False`, only items which have no
                               `order_amount` specified are let through.
        """

        order_discounts = kwargs.get('order_discounts', None)

        superclass = super(OrderDiscountAmountMixin, cls)
        valid = superclass.get_valid_discounts(**kwargs)

        if not order_discounts is None:
            # If an order discounts criterium has been specified
            all_discounts = cls.get_all_discounts()
            valid = valid | \
                all_discounts.filter(order_amount__isnull=not order_discounts)

        return valid

    def get_discount(self, **kwargs):
        """
        Get the total amount of discount for the current item.
        """
        superclass = super(OrderDiscountAmountMixin, self)

        discount = superclass.get_discount(**kwargs)
        if self.order_amount:
            discount += self.order_amount

        return discount

    def __unicode__(self):
        return _(u'%s on order') % self.order_amount


class ItemDiscountAmountMixin(models.Model):
    """
    Mixin for absolute amount discounts, valid only for the particular
    items in this order.
    """

    class Meta:
        abstract = True

    item_amount = PriceField(verbose_name=_('item discount amount'),
                             null=True, blank=True)
    """
    Absolute discount for items of an order for which this discount
    is valid.
    """

    @classmethod
    def get_valid_discounts(cls, **kwargs):
        """
        We want to be able to discriminate between discounts valid for
        the whole order and those valid for order items.

        :param item_discounts: When `True`, only items for which
                               `item_amount` has been specified are valid.
                               When `False`, only items which have no
                               `item_amount` specified are let through.
        """

        item_discounts = kwargs.get('item_discounts', None)

        superclass = super(ItemDiscountAmountMixin, cls)
        valid = superclass.get_valid_discounts(**kwargs)

        if not item_discounts is None:
            all_discounts = cls.get_all_discounts()

            # If an order discounts criterium has been specified
            valid = valid | \
                all_discounts.filter(item_amount__isnull=not item_discounts)

        return valid

    def get_discount(self, **kwargs):
        """
        Get the total amount of discount for the current item.
        """
        superclass = super(ItemDiscountAmountMixin, self)

        discount = superclass.get_discount(**kwargs)
        if self.item_amount:
            discount += self.item_amount

        return discount

    def __unicode__(self):
        return _(u'%s on order item') % self.item_amount


class OrderDiscountPercentageMixin(models.Model):
    """
    Mixin for discounts which apply as a percentage from the total
    order amount.
    """

    class Meta:
        abstract = True

    order_percentage = PercentageField(verbose_name=\
                                        _('order discount percentage'),
                                       null=True, blank=True)
    """ Percentual discount on the total of an order. """

    @classmethod
    def get_valid_discounts(cls, **kwargs):
        """
        We want to be able to discriminate between discounts valid for
        the whole order and those valid for order items.

        :param order_discounts: When `True`, only items for which
                               `order_amount` has been specified are valid.
                               When `False`, only items which have no
                               `order_amount` specified are let through.
        """

        order_discounts = kwargs.get('order_discounts', None)

        superclass = super(OrderDiscountPercentageMixin, cls)
        valid = superclass.get_valid_discounts(**kwargs)

        if not order_discounts is None:
            all_discounts = cls.get_all_discounts()

            # If an order discounts criterium has been specified
            valid = valid | \
                all_discounts.filter(order_percentage__isnull=not order_discounts)

        return valid

    def get_discount(self, **kwargs):
        """
        Get the total amount of discount for the current item.
        """

        order_price = kwargs.get('order_price')

        superclass = super(OrderDiscountPercentageMixin, self)

        discount = superclass.get_discount(**kwargs)

        if self.order_percentage:
            discount += (self.order_percentage/100)*order_price

        return discount

    def __unicode__(self):
        return _(u'%s%% on order') % self.order_percentage


class ItemDiscountPercentageMixin(models.Model):
    """
    Mixin for percentual discounts, valid only for the particular
    items in this order.
    """

    class Meta:
        abstract = True

    item_percentage = PercentageField(verbose_name=\
                                        _('item discount percentage'),
                                      null=True, blank=True)
    """
    Percentual discount for items of an order for which this discount
    is valid.
    """


    @classmethod
    def get_valid_discounts(cls, **kwargs):
        """
        We want to be able to discriminate between discounts valid for
        the whole order and those valid for order items.

        :param item_discounts: When `True`, only items for which
                               `item_amount` has been specified are valid.
                               When `False`, only items which have no
                               `item_amount` specified are let through.
        """

        item_discounts = kwargs.get('item_discounts', None)

        superclass = super(ItemDiscountPercentageMixin, cls)
        valid = superclass.get_valid_discounts(**kwargs)

        if not item_discounts is None:
            all_discounts = cls.get_all_discounts()

            # If an order discounts criterium has been specified
            valid = valid | \
                all_discounts.filter(item_percentage__isnull=not item_discounts)

        return valid

    def get_discount(self, **kwargs):
        """
        Get the total amount of discount for the current item.
        """

        item_price = kwargs.get('item_price')

        superclass = super(ItemDiscountPercentageMixin, self)

        discount = superclass.get_discount(**kwargs)
        if self.item_percentage:
            discount += (self.item_percentage/100)*item_price

        return discount

    def __unicode__(self):
        return _(u'%s on order item') % self.item_percentage


class ProductDiscountMixin(models.Model):
    """ Mixin defining a discount valid for a single product. """

    class Meta:
        abstract = True

    product = models.ForeignKey(PRODUCT_MODEL, db_index=True,
                                blank=True, null=True,
                                verbose_name=_('product'))
    """ Product this discount relates to. """

    @classmethod
    def get_valid_discounts(cls, **kwargs):
        """ Return valid discounts for a specified product """

        superclass = super(ProductDiscountMixin, cls)
        valid = superclass.get_valid_discounts(**kwargs)

        product = kwargs.get('product', None)
        # When a product has been specified, allow discounts for this
        # specific product and discounts for which no product is specified
        valid = valid.filter(Q(product__isnull=True) | Q(product=product))

        return valid


class ManyProductDiscountMixin(models.Model):
    """ Mixin defining discounts based on products. """

    class Meta:
        abstract = True

    products = models.ManyToManyField(PRODUCT_MODEL, db_index=True,
                                blank=True, null=True,
                                verbose_name=_('products'))
    """ Products this discount relates to. """

    @classmethod
    def get_valid_discounts(cls, **kwargs):
        """ Return valid discounts for a specified product """

        superclass = super(ManyProductDiscountMixin, cls)
        valid = superclass.get_valid_discounts(**kwargs)

        # Note: products=product here might be wrong -> products__in=product
        product = kwargs.get('product', None)
        # When a product has been specified, allow discounts for this
        # specific product and discounts for which no product is specified
        valid = valid.filter(products=product) | \
                valid.filter(products__isnull=True)

        return valid


class DateRangeDiscountMixin(models.Model):
    """ Mixin for discount which are only valid within a given date range. """

    class Meta:
        abstract = True

    start_date = models.DateField(verbose_name=_('start date'),
                                  db_index=True, null=True, blank=True,
                                help_text=_('If not left blank, this \
                                  specifies a start date for the validity \
                                  of this discount.'))
    end_date = models.DateField(verbose_name=_('end date'),
                                db_index=True, null=True, blank=True,
                                help_text=_('If not left blank, this \
                                  specifies an end date for the validity \
                                  of this discount.'))

    @classmethod
    def get_valid_discounts(cls, **kwargs):
        """
        Return valid discounts for a specified date, taking the current
        date if no date is specified. When no start or end date are specified,
        a discount defaults to be valid.

        .. todo::
            Test this code.
        """

        superclass = super(DateRangeDiscountMixin, cls)
        valid = superclass.get_valid_discounts(**kwargs)

        date = kwargs.get('date', None)
        # If no date is set, take today.
        if not date:
            date = datetime.today()

        # Get valid discounts for the current situation
        valid = valid.filter(
                    Q(start_date__isnull=True, end_date__isnull=True) | \
                    Q(start_date__isnull=True, end_date__lte=date) | \
                    Q(start_date__gte=date, end_date__isnull=True) | \
                    Q(start_date__gte=date, end_date__lte=date))

        return valid


try:
    from webshop.extensions.category.settings import CATEGORY_MODEL
    CATEGORIES = True
except ImportError:
    # Apparantly, no category model is defined for this webshop
    CATEGORIES = False
    logger.info(u'No category model defined, not loading category discounts.')


if CATEGORIES:
    class CategoryDiscountMixin(models.Model):
        """ Mixin defining discounts based on a single category. """

        class Meta:
            abstract = True

        category = models.ForeignKey(CATEGORY_MODEL, db_index=True,
                                     blank=True, null=True,
                                     verbose_name=_('category'))
        """ Category this discount relates to. """

        @classmethod
        def get_valid_discounts(cls, **kwargs):
            """ Return valid discounts for a specified product """

            superclass = super(CategoryDiscountMixin, cls)
            valid = superclass.get_valid_discounts(**kwargs)

            category = kwargs.get('category', None)
            valid = valid.filter(Q(category__isnull=True) | \
                                 Q(category=category))

            return valid


    class ManyCategoryDiscountMixin(models.Model):
        """ Mixin defining discounts based on a collection of categories. """

        class Meta:
            abstract = True

        categories = models.ManyToManyField(CATEGORY_MODEL, db_index=True,
                                            blank=True, null=True,
                                            verbose_name=_('categories'))
        """ Categories this discount relates to. """

        @classmethod
        def get_valid_discounts(cls, **kwargs):
            """ Return valid discounts for a specified product """

            superclass = super(ManyCategoryDiscountMixin, cls)
            valid = superclass.get_valid_discounts(**kwargs)

            category = kwargs.get('category', None)
            valid = valid.filter(Q(categories__isnull=True) | \
                                 Q(categories=category))


            return valid


class CouponDiscountMixin(models.Model):
    """ Discount based on a specified coupon code. """

    class Meta:
        abstract = True

    use_coupon = models.BooleanField(default=False)
    coupon_code = models.CharField(verbose_name=_('coupon code'), null=True,
                                   max_length=COUPON_LENGTH, blank=True,
                                   help_text=_('If left empty and a coupon \
                                                is used, a code will \
                                                be automatically generated.'),
                                   db_index=True)
    """ Code for this coupon, which will be automatically generated upon saving. """

    @staticmethod
    def generate_coupon_code():
        """
        Generate a coupon code of `COUPON_LENGHT` characters consisting
        of the characters in `COUPON_CHARACTERS`.

        .. todo::
            Unittest this function.

        """
        import random

        rndgen = random.random()
        random.seed()

        code = ''

        while len(code) < COUPON_LENGTH:
            # Select a random character from COUPON_CHARACTERS and add it to
            # the code.
            code += COUPON_CHARACTERS[random.randint(0, len(COUPON_CHARACTERS)-1)]

        logger.debug(u'Generated coupon code \'%s\'', code)

        return code


    def save(self):
        if self.use_coupon and not self.coupon_code:
            self.coupon_code = self.generate_coupon_code()

        super(CouponDiscountMixin, self).save()

    @classmethod
    def get_valid_discounts(cls, coupon_code=None, **kwargs):
        """
        Return only items for which no coupon code has been set or
        ones for which the current coupon code matches that of the
        discounts.

        .. todo::
            Write tests for this.
        """

        superclass = super(CouponDiscountMixin, cls)
        valid = superclass.get_valid_discounts(**kwargs)

        if coupon_code:
            valid = valid.filter(Q(coupon_code__isnull=True) | \
                                 Q(use_coupon=True, coupon_code=coupon_code)
                                )
        else:
            valid = valid.filter(coupon_code__isnull=True)

        return valid


class AccountedUseDiscountMixin(models.Model):
    """
    Mixin class for discounts for which the number of uses is accounted.

    ..todo::
        Make sure our Order API has hooks for 'completed orders' and this one
        attaches to these. We probably want to use signals for this one.
    """

    class Meta:
        abstract = True

    used = models.PositiveSmallIntegerField(verbose_name=_('times used'),
                                            default=0, db_index=True)
    """ The number of times this discount has been used. """

    @classmethod
    def register_use(cls, qs, count=1):
        """ Register `count` uses of discounts in queryset `qs`. """
        qs.update(used=models.F('used') + count)

    # def register_use(self, count=1):
    #     """
    #     Register the usage of this particular discount, effectively
    #     adding `count` to the used property.
    #
    #     As the register_use classmethod for querysets is (much) more
    #     efficient, in practice, this method has been deprecated.
    #     """
    #     self.used = models.F('used') + count
    #     self.save()


class LimitedUseDiscountMixin(AccountedUseDiscountMixin):
    """
    Mixin class for discounts which can only be used a limited number
    of times.
    """

    class Meta:
        abstract = True

    use_limit = models.PositiveSmallIntegerField(verbose_name=_('use limit'),
                                                 blank=True, null=True,
                                                 db_index=True,
                                                 help_text= \
                      _('Maximum number of times this discount may be used.'))
    """
    The maximum number of times this discount may be used. If this value is
    not given, no limit is imposed.
    """

    def get_uses_left(self):
        """ Return the amount of uses left. """
        leftover = self.use_limit - self.used

        assert leftover >= 0

        return leftover

    @classmethod
    def get_valid_discounts(cls, **kwargs):
        """
        Return currently valid discounts: ones for which either no use
        limit has been set or for which the amount of uses lies under the
        limit.
        """

        superclass = super(LimitedUseDiscountMixin, cls)
        valid = superclass.get_valid_discounts(**kwargs)

        valid = valid.filter(Q(use_limit__isnull=True) | \
                             Q(use_limit__gt=models.F('used')))

        return valid
