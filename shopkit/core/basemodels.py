# Copyright (C) 2010-2011 Mathijs de Bruin <mathijs@mathijsfietst.nl>
#
# This file is part of django-shopkit.
#
# django-shopkit is free software; you can redistribute it and/or modify
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

import datetime

from django.utils.translation import ugettext_lazy as _
from django.db import models

from shopkit.core.settings import MAX_NAME_LENGTH
from shopkit.core.managers import ActiveItemManager

"""
Generic abstract base classes for:
* :class:`Customers <shopkit.core.basemodels.AbstractCustomerBase>`

"""


class AbstractCustomerBase(models.Model):
    """ Abstract base class for customers of the shop. """

    class Meta:
        verbose_name = _('customer')
        verbose_name_plural = _('customers')
        abstract = True

    def get_all_orders(self):
        """ Get all orders by the customer """
        return self.order_set.all()

    def get_confirmed_orders(self):
        """
        Get all completed orders for this customer

        .. todo::
            We should consider adding a manager to :class:`OrderBase` which
            can filter on the completed states.
        """
        orders = self.get_all_orders()

        completed = orders.filter(confirmed=True)

        return completed

    def get_latest_order(self):
        """ Return the lastest confirmed order """
        completed = self.get_confirmed_orders()

        try:
            return completed.order_by('-date_added')[0]
        except IndexError:
            return None


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


def get_next_ordering(qs, ordering_increase=10):
    max_ordering = qs.aggregate(models.Max('sort_order'))['sort_order__max']

    if max_ordering:
        return max_ordering+ordering_increase
    else:
        return ordering_increase


class OrderedItemBase(models.Model):
    """
    Abstract base class for items that have explicit ordering.
    """

    class Meta:
        abstract = True
        ordering = ('sort_order', )

    @classmethod
    def get_next_ordering(cls):
        return get_next_ordering(cls.objects.all())

    def save(self):
        """
        If no `sort_order` has been specified, make sure we calculate the
        it based on the highest available current `sort_order`.
        """

        if not self.sort_order:
            self.sort_order = self.get_next_ordering()

        super(OrderedItemBase, self).save()

    sort_order = models.PositiveIntegerField(
                                 verbose_name=('sort order'),
                                 unique=True, blank=True, db_index=True,
                                 help_text=_('Change this to alter the order \
                                              in which items are displayed.'))


class OrderedInlineItemBase(models.Model):
    """
    This base class does what, actually, order_with_respect_to should do
    but (for now) doesn't implement very well: ordering of objects with
    a fk-relation to some class.

    As we do not know what the class with the respective relation is, it
    is important to note that something like the following is added::

        class MyOrderedInline(OrderedInlineItemBase):

            <related> = models.ForeignKey(RelatedModel)

            class Meta(OrderedInlineItemBase.Meta):
                unique_together = ('sort_order', '<related>')

            def get_related_ordering(self):
                return self.__class__.objects.filter(<related>=self.<related>)



        ... Or we could simply wait for the Django developers to fix
        `order_with_respect_to` once and for all. (Work in progress...
        See `Ticket #13 <http://code.djangoproject.com/ticket/13>`.)


    """

    def get_related_ordering(self):
        """
        Get a :class:`QuerySet <django.db.models.QuerySet.QuerySet`
        with related items to be considered for calculating the next
        `sort_order`.

        As we do not know in this base class what the related field(s)
        are, this raises a NotImplementedError. It should be subclassed
        with something like::

            return self.objects.filter(<related>=self.<related>)

        """
        raise NotImplementedError

    @staticmethod
    def get_next_ordering(related):
        """
        Get the next ordering based upon the :class:`QuerySet <django.db.models.QuerySet.QuerySet`
        with related items.
        """
        return get_next_ordering(related)

    def save(self):
        """
        If no `sort_order` has been specified, make sure we calculate the
        it based on the highest available current `sort_order`.
        """

        if not self.sort_order:
            related = self.get_related_ordering()
            self.sort_order = self.get_next_ordering(related)

            logger.debug(u'Generated sort_order %d for object %s',
                self.sort_order, self)


        super(OrderedInlineItemBase, self).save()


    class Meta:
        abstract = True
        ordering = ('sort_order', )

    sort_order = models.PositiveSmallIntegerField(
                                 verbose_name=('sort order'),
                                 blank=True, db_index=True,
                                 help_text=_('Change this to alter the order \
                                              in which items are displayed.'))



class ActiveItemBase(models.Model):
    """
    Abstract base class for items which can be activated or deactivated.
    """

    class Meta:
        abstract = True

    active = models.BooleanField(verbose_name=_('active'),
                                 default=True, db_index=True)
    """ Whether the item is active in the frontend. """


class ActiveItemInShopBase(ActiveItemBase):
    """
    This is a subclass of :class:`ActiveItemBase` with an
    :class:`ActiveItemManager <shopkit.core.managers.ActiveItemManager>` called `in_shop`.

    The main purpose of this class is allowing for items to be enabled or
    disabled in the shop's frontend
    """

    class Meta:
        abstract = True

    objects = models.Manager()
    in_shop = ActiveItemManager()
    """ An instance of :class:`ActiveItemManager <shopkit.core.managers.ActiveItemManager>`,
        returning only items with `active=True`.
    """


class DatedItemBase(models.Model):
    """
    Item for which the add and modification date are automatically
    tracked.
    """

    class Meta:
        abstract = True
        ordering = ['-date_added', '-date_modified']
        get_latest_by = 'date_added'

    date_added = models.DateTimeField(auto_now_add=True,
                                      verbose_name=_('creation date'))
    date_modified = models.DateTimeField(auto_now=True,
                                         verbose_name=_('modification date'))


class PublishDateItemBase(models.Model):
    """ Item with a publish date. """

    class Meta:
        abstract = True
        ordering = ['-date_publish']
        get_latest_by = 'date_publish'

    date_publish = models.DateTimeField(default=datetime.datetime.now(),
                                        verbose_name=_('publication date'),
                                        db_index=True)


class NumberedOrderBase(models.Model):
    """ Base class for `Order` with invoice and order numbers. """

    class Meta:
        abstract = True

    invoice_number = models.SlugField(_('invoice number'), db_index=True,
                                      editable=False, max_length=255,
                                      unique=True, null=True, default=None)
    order_number = models.SlugField(_('order number'), db_index=True,
                                    editable=False, max_length=255,
                                    unique=True)

    def generate_invoice_number(self):
        """
        Generates an invoice number for the current order. Should be
        overridden in subclasses.
        """
        raise NotImplementedError

    def generate_order_number(self):
        """
        Generates an order number for the current order. Should be
        overridden in subclasses.
        """
        raise NotImplementedError

    def save(self, *args, **kwargs):
        """ Generate an order number upon saving the order. """

        if not self.order_number:
            self.order_number = self.generate_order_number()

            logger.debug('Generated order number %s for %s',
                         self.order_number, self.order_number)

        super(NumberedOrderBase, self).save(*args, **kwargs)

    def confirm(self):
        """ Make sure we set an invoice number upon order confirmation. """

        super(NumberedOrderBase, self).confirm()

        assert not self.invoice_number
        self.invoice_number = self.generate_invoice_number()

        logger.debug('Generated invoice number %s for %s',
                     self.invoice_number, self.order_number)

        # Note: This save operation might not me necessary
        self.save()


