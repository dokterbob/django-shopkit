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

DISCOUNT_MODEL = getattr(settings, 'WEBSHOP_DISCOUNT_MODEL')
""" Model used for product discounts. """

COUPON_LENGTH = getattr(settings, 'WEBSHOP_COUPON_LENGTH', 20)
""" Length of a coupon code. """

COUPON_CHARACTERS = getattr(settings, 'WEBSHOP_COUPON_CHARACTERS', '23456789QWERTASDFGZXCVBYUIPHJKLNM')
""" Characters used for generating coupon codes.
    This defaults to: `23456789QWERTASDFGZXCVBYUIPHJKLNM`

    .. note::
        Make sure each character only appears once in this string, or
        the security of your coupon codes might weaken.

"""
