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

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

STOCK_CHOICES = getattr(settings, 'SHOPKIT_STOCK_CHOICES', 
                    ((0, _('Available')),
                     (1, _('Not available')), ))
"""
Available choices for the `stock` field of 
:class:`StockedItems <shopkit.stock.simple.models.StockedItem>`.
"""

STOCK_DEFAULT = getattr(settings, 'SHOPKIT_STOCK_DEFAULT', 0) 
"""
Default
choice for the `stock` field of :class:`StockedItems
<shopkit.stock.simple.models.StockedItem>`.
"""

STOCK_ORDERABLE = getattr(settings, 'SHOPKIT_STOCK_ORDERABLE', (0, ))
""" 
An iterable with choices from `STOCK_CHOICES` which represent orderable states
-- states which will not raise an exception when saving the shopping cart.
"""

