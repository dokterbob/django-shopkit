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

from webshop.extensions.shipping.settings import ADDRESS_MODEL

class ShippedOrderMixin(models.Model):
    class Meta:
        abstract = True

    shipping_address = models.ForeignKey(ADDRESS_MODEL, 
                                        related_name='shippable%(class)s_set')


class ShippedCustomerMixin(object):
    """
    Customer Mixin class for shops in which orders make use
    of a shipping address.
    """

    def get_recent_shipping(self):
        """ Return the most recent shipping address """
        latest_order = self.get_latest_order()

        return latest_order.shipping_address

