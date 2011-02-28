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
from webshop.core.basemodels import AbstractPricedItemBase
from webshop.core.utils import get_model_from_string
from webshop.core.utils.fields import PercentageField

# Get the currently configured currency field, whatever it is
from webshop.extensions.currency.utils import get_currency_field
PriceField = get_currency_field()

from webshop.extensions.discounts.settings import *


class DiscountedItemMixin(AbstractPricedItemBase):
    """ Mixin class for discounted items. """

    def get_valid_discounts(self, **kwargs):
        """ Return valid discounts for the current order. """
        discount_class = get_model_from_string(DISCOUNT_MODEL)

        discounts = discount_class.get_valid_discounts(**kwargs)

        return discounts

    def get_discount(self, **kwargs):
        """
        Get the discount for the current item. Should be overridden
        in subclasses.
        """
        raise NotImplementedError

    def get_discounted_price(self, **kwargs):
        """ Get the current price with discount applied. """

        return self.get_price(**kwargs) - self.get_discount(**kwargs)


class DiscountedOrderBase(DiscountedItemMixin, models.Model):
    """ Base class for orders with a discount. """

    class Meta:
        abstract = True

    def get_valid_discounts(self, **kwargs):
        """ Return valid discounts for the current order. """
        superclass = super(DiscountedOrderBase, self)
        return superclass.get_valid_discounts(order_discounts=True, **kwargs)

    def get_discount(self, **kwargs):
        """
        Get the total discount for this Order.

        ..todo::
            Persistent storage of the discount amount on the order -
            and making sure it automatically updates when this is needed.
        """

        # First, get discounts on order items

        # We might optimize this, considering that we eventually want to
        # store all discount quantities directly in the database.
        # This is fairly safe as long as we provide proper save hooks.
        total_discount = 0.0
        for item in self.orderitem_set.all():
            total_discount += item.get_discount(**kwargs)

        # Now, add discounts on the total order
        valid_discounts = self.get_valid_discounts(**kwargs)
        order_price = self.get_price(**kwargs)

        for discount in valid_discounts:
            total_discount += discount.get_discount(order_price=order_price,
                                                    **kwargs)

        # Make sure the discount is never higher than the price of the oringal
        # item
        if total_discount > order_price:
            total_discount = order_price

        return total_discount


class DiscountCouponOrderBase(DiscountedOrderBase):
    """ Order with a coupon code. """

    class Meta:
        abstract = True

    coupon_code = models.CharField(verbose_name=_('coupon code'), null=True,
                                   max_length=COUPON_LENGTH, blank=True)
    """ Coupon code entered for the current order. """

    def get_valid_discounts(self, **kwargs):
        """ Return valid discounts for the current order. """
        superclass = super(DiscountCouponOrderBase, self)
        return superclass.get_valid_discounts(coupon_code=self.coupon_code,
                                              **kwargs)


class DiscountedOrderItemBase(DiscountedItemMixin, models.Model):
    """ Base class for orderitems which can have discounts applied to them.  """

    class Meta:
        abstract = True

    def get_valid_discounts(self, **kwargs):
        """ Return valid discounts for the current order. """
        superclass = super(DiscountedOrderItemBase, self)
        return superclass.get_valid_discounts(product=self.product,
                                              item_discounts=True,
                                              **kwargs)


    def get_discount(self, **kwargs):
        """
        Get the total discount for this OrderItem.

        ..todo::
            Persistent storage of the discount amount on the order -
            and making sure it automatically updates when this is needed.

        """

        valid_discounts = self.get_valid_discounts(**kwargs)
        item_price = self.product.get_price(**kwargs)

        total_discount = 0.0
        for discount in valid_discounts:
            total_discount += discount.get_discount(item_price=item_price, **kwargs)

        # Make sure the discount is never higher than the price of the oringal
        # item
        if total_discount > item_price:
            total_discount = item_price

        return total_discount


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

        raise cls.objects.all()

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
        raise NotImplementedError


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
    def get_valid_discounts(cls, order_discounts=None, **kwargs):
        """
        We want to be able to discriminate between discounts valid for
        the whole order and those valid for order items.

        :param order_discounts: When `True`, only items for which
                               `order_amount` has been specified are valid.
                               When `False`, only items which have no
                               `order_amount` specified are let through.
        """

        superclass = super(OrderDiscountAmountMixin, self)
        valid = superclass.get_valid_discounts(**kwargs)

        if not order_discounts is None:
            # If an order discounts criterium has been specified
            valid = valid.filter(order_amount__isnull=not order_discounts)

        return valid

    def get_discount(self, **kwargs):
        """
        Get the total amount of discount for the current item.
        """
        superclass = super(OrderDiscountAmountMixin, self)

        discount = superclass.get_discount(**kwargs)
        discount += self.order_amount

        return discount


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
    def get_valid_discounts(cls, item_discounts=None, **kwargs):
        """
        We want to be able to discriminate between discounts valid for
        the whole order and those valid for order items.

        :param item_discounts: When `True`, only items for which
                               `item_amount` has been specified are valid.
                               When `False`, only items which have no
                               `item_amount` specified are let through.
        """

        superclass = super(ItemDiscountAmountMixin, self)
        valid = superclass.get_valid_discounts(**kwargs)

        if not item_discounts is None:
            # If an order discounts criterium has been specified
            valid = valid.filter(item_amount__isnull=not item_discounts)

        return valid

    def get_discount(self, **kwargs):
        """
        Get the total amount of discount for the current item.
        """
        superclass = super(ItemDiscountAmountMixin, self)

        discount = superclass.get_discount(**kwargs)
        discount += self.item_amount

        return discount


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
    def get_valid_discounts(cls, order_discounts=None, **kwargs):
        """
        We want to be able to discriminate between discounts valid for
        the whole order and those valid for order items.

        :param order_discounts: When `True`, only items for which
                               `order_amount` has been specified are valid.
                               When `False`, only items which have no
                               `order_amount` specified are let through.
        """

        superclass = super(OrderDiscountPercentageMixin, self)
        valid = superclass.get_valid_discounts(**kwargs)

        if not order_discounts is None:
            # If an order discounts criterium has been specified
            valid = valid.filter(order_percentage__isnull=not order_discounts)

        return valid

    def get_discount(self, order_price, **kwargs):
        """
        Get the total amount of discount for the current item.
        """
        superclass = super(OrderDiscountPercentageMixin, self)

        discount = superclass.get_discount(**kwargs)
        discount += (self.order_percentage/100)*order_price

        return discount


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
    def get_valid_discounts(cls, item_discounts=None, **kwargs):
        """
        We want to be able to discriminate between discounts valid for
        the whole order and those valid for order items.

        :param item_discounts: When `True`, only items for which
                               `item_amount` has been specified are valid.
                               When `False`, only items which have no
                               `item_amount` specified are let through.
        """

        superclass = super(ItemDiscountPercentageMixin, self)
        valid = superclass.get_valid_discounts(**kwargs)

        if not item_discounts is None:
            # If an order discounts criterium has been specified
            valid = valid.filter(item_percentage__isnull=not item_discounts)

        return valid

    def get_discount(self, item_price, **kwargs):
        """
        Get the total amount of discount for the current item.
        """
        superclass = super(ItemDiscountPercentageMixin, self)

        discount = superclass.get_discount(**kwargs)
        discount += (self.item_percentage/100)*item_price

        return discount


class ProductDiscountMixin(models.Model):
    """ Mixin defining a discount on a single product. """

    class Meta:
        abstract = True

    product = models.ForeignKey(PRODUCT_MODEL, db_index=True,
                                blank=True, null=True,
                                verbose_name=_('product'))
    """ Product this discount relates to. """

    @classmethod
    def get_valid_discounts(cls, product, **kwargs):
        """ Return valid discounts for a specified product """

        valid = \
            super(ProductDiscountMixin, self).get_valid_discounts(**kwargs)

        valid = valid.filter(product=product) | \
                valid.filter(product__isnull=True)

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
    def get_valid_discounts(cls, product, **kwargs):
        """ Return valid discounts for a specified product """

        valid = \
            super(ProductDiscountMixin, self).get_valid_discounts(**kwargs)

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
    def get_valid_discounts(cls, date=None, **kwargs):
        """
        Return valid discounts for a specified date, taking the current
        date if no date is specified. When no start or end date are specified,
        a discount defaults to be valid.

        .. todo::
            Test this code.
        """

        valid = \
            super(DateRangeDiscountMixin, self).get_valid_discounts(**kwargs)

        # If no date is set, take today.
        if not date:
            date = datetime.datetime.today()

        # Get valid discounts for the current situation
        valid = valid.filter(start_date__gte=date, end_date__lte=date) | \
                valid.filter(start_date__isnull=True, end_date__lte=date) | \
                valid.filter(start_date__gte=date, end_date__isnull=True) | \
                valid.filter(start_date__isnull=True, end_date__isnull=True)

        return valid


try:
    from webshop.extensions.category.settings import CATEGORY_MODEL
    CATEGORIES = True
except ImportError:
    # Apparantly, no category model is defined for this webshop
    CATEGORIES = False
    logger.info('No category model defined, not loading category discounts.')


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
        def get_valid_discounts(cls, category, **kwargs):
            """ Return valid discounts for a specified product """

            valid = \
                super(CategoryDiscountMixin, self).get_valid_prices(**kwargs)

            valid = valid.filter(category=category) | \
                    valid.filter(category__isnull=True)

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
        def get_valid_discounts(cls, category, **kwargs):
            """ Return valid discounts for a specified product """

            valid = \
                super(ManyCategoryDiscountMixin, self).get_valid_prices(**kwargs)

            valid = valid.filter(categories=category) | \
                    valid.filter(categories__isnull=True)

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
        import random

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

        valid = \
            super(CouponDiscountMixin, self).get_valid_discounts(**kwargs)

        if coupon_code:
            valid = valid.filter(coupon_code=coupon_code) | \
                    valid.filter(coupon_code__isnull=True)
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
                                            default=0)
    """ The number of times this discount has been used. """

    def register_use(self, count=1):
        """
        Register the usage of this particular discount, effectively
        adding `count` to the used property.

        .. todo::
            We might as well use Django's hip method of updating this value
            without actually requiring the current value to be known.
        """
        self.used += 1
        # self.used = models.F('used) + 1
        self.save()


class LimitedUseDiscountMixin(AccountedUseDiscountMixin):
    """
    Mixin class for discounts which can only be used a limited number
    of times.
    """

    class Meta:
        abstract = True

    use_limit = models.PositiveSmallIntegerField(verbose_name=_('use limit'),
                                                 blank=True, null=True,
                                                 help_text= \
                      _('Maximum number of times this discount may be used.'))
    """
    The maximum number of times this discount may be used. If this value is
    not given, no limit is imposed.
    """

    @classmethod
    def get_valid_discounts(cls, **kwargs):
        """
        Return currently valid discounts: ones for which either no use
        limit has been set or for which the amount of uses lies under the
        limit.

        .. todo::
            Write tests for this.
        """

        valid = \
            super(LimitedUseDiscountMixin, self).get_valid_discounts(**kwargs)

        valid = valid.filter(use_limit__lte=models.F('used'))| \
                valid.filter(use_limit__isnull=True)

        return valid

