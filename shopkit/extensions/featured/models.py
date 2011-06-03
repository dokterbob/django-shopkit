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

from django.db import models
from django.utils.translation import ugettext_lazy as _


class FeaturedProductMixin(models.Model):
    """
    Mixin for products which have a boolean featured property and an
    `is_featured` manager, filtering the items from the `in_shop` manager
    so that only featured items are returned.

    .. todo::
        Write the `is_featured` manager - and test it.

    """

    class Meta:
        abstract = True

    featured = models.BooleanField(_('featured'), default=False,
                               help_text=_('Whether this product will be \
                               shown on the shop\'s frontpage.'))
    """ Whether or not this product is featured in the shop. """


class OrderedFeaturedProductMixin(FeaturedProductMixin):
    """
    Mixin for ordered featured products.
    
    .. todo::
        Make sure the `is_featured` manager for this base model uses the 
        `featured_order` attribute.
    """

    class Meta:
        abstract = True

    featured_order = models.PositiveSmallIntegerField(_('featured order'),
                                        blank=True, null=True)
    """ The order in which featured items are ordered when displayed. """
