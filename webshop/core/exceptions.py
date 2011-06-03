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

from django.utils.translation import ugettext_lazy as _


class WebshopExceptionBase(Exception):
    """ Base class for exception in django-shopkit. """
    pass


class AlreadyConfirmedException(Exception):
    """
    Exception raised when confirmation is attempted for an order which has
    already been confirmed.
    """

    def __init__(self, order):
        self.order = order

    def __str__(self):
        return _('Order %s has already been confirmed') % self.order