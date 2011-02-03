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

from webshop.core.exceptions import WebshopExceptionBase

class NoStockAvailableException(WebshopExceptionBase):
    """ 
    Exception raised by the save method of :class:`StockedCartItemMixinBase` 
    when no stock is available for the current item.
    """
    
    def __init__(self, item):
        self.item = item
    
    def __unicode__(self):
        return u'No stock available for item \'%s\'' % self.item
