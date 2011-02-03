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

from django.utils.translation import ugettext_lazy as _
from django.db import models

from webshop.core.settings import MAX_NAME_LENGTH
from webshop.core.managers import ActiveItemManager

"""
Generic abstract base classes for:
* :class:`Customers <webshop.core.basemodels.AbstractCustomerBase>`

"""


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

    sort_order = models.PositiveSmallIntegerField(
                                 verbose_name=('sort order'),
                                 unique=True, blank=True,
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
            
            logger.debug('Generated sort_order %d for object %s',
                self.sort_order, self)

        
        super(OrderedInlineItemBase, self).save()


    class Meta:
        abstract = True
        ordering = ('sort_order', )

    sort_order = models.PositiveSmallIntegerField(
                                 verbose_name=('sort order'),
                                 blank=True,
                                 help_text=_('Change this to alter the order \
                                              in which items are displayed.'))



class ActiveItemBase(models.Model):
    """
    Abstract base class for items which can be activated or deactivated.
    """

    class Meta:
        abstract = True

    active = models.BooleanField(verbose_name=_('active'),
                                 default=True)
    """ Whether the item is active in the frontend. """


class ActiveItemInShopBase(ActiveItemBase):
    """
    This is a subclass of :class:`ActiveItemBase` with an
    :class:`ActiveItemManager <webshop.core.managers.ActiveItemManager>` called `in_shop`.

    The main purpose of this class is allowing for items to be enabled or
    disabled in the shop's frontend
    """

    class Meta:
        abstract = True

    objects = models.Manager()
    in_shop = ActiveItemManager()
    """ An instance of :class:`ActiveItemManager <webshop.core.managers.ActiveItemManager>`,
        returning only items with `active=True`.
    """


class DatedItemBase(models.Model):

    class Meta:
        abstract = True
        ordering = ['-date_added', '-date_modified']
        get_latest_by = 'date_added'

    date_added = models.DateTimeField(auto_now_add=True,
                                      verbose_name=_('date added'))
    date_modified = models.DateTimeField(auto_now=True,
                                       verbose_name=_('date modified'))

