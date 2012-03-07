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

CUSTOMER_MODEL = getattr(settings, 'SHOPKIT_CUSTOMER_MODEL', None)
""" Reference to the customer model used in the shop. """

PRODUCT_MODEL = getattr(settings, 'SHOPKIT_PRODUCT_MODEL')
""" Reference to the model class defining the product. """

CART_MODEL = getattr(settings, 'SHOPKIT_CART_MODEL')
""" The model used for shopping carts. """

CARTITEM_MODEL = getattr(settings, 'SHOPKIT_CARTITEM_MODEL')
""" The model used for shopping cart items. """

ORDER_MODEL = getattr(settings, 'SHOPKIT_ORDER_MODEL')
""" The model used for orders. """

ORDER_STATES = getattr(settings, 'SHOPKIT_ORDER_STATES')
"""
Mapping for order states of the following form::

    SHOPKIT_ORDER_STATES = (
        (00, _('Temp')),
        (10, _('New')),
        (20, _('Blocked')),
        (30, _('In Process')),
        (40, _('Billed')),
        (50, _('Shipped')),
        (60, _('Complete')),
        (70, _('Cancelled')),
    )

"""

DEFAULT_ORDER_STATE = getattr(settings, 'SHOPKIT_DEFAULT_ORDER_STATE', ORDER_STATES[0][0])
""" 
Default state for new orders. By default, the first state in 
`SHOPKIT_ORDER_STATES` is selected.
"""

ORDERSTATE_CHANGE_MODEL = getattr(settings, 'SHOPKIT_ORDERSTATE_CHANGE_MODEL')
""" Model used for logging state changes of orders. """

ORDERITEM_MODEL = getattr(settings, 'SHOPKIT_ORDERITEM_MODEL')
""" The model used for order items. """

MAX_NAME_LENGTH = getattr(settings, 'SHOPKIT_MAX_NAME_LENGTH', 255)
""" (Optional) The maximum name length for named products in the webshop. 
    This defaults to 255.
"""