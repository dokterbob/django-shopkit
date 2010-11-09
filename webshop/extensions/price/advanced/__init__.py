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

"""
The model structure in this extension is very preliminary. Ideally, one would
want all ones prices to reside in a single table.

One way to approach this would be using a private function `_get_valid` for
`PriceBase` subclasses and then implementing a `get_valid` in `PriceBase` which
calls the `_get_valid` functions for direct parent classes that inherit from
`PriceBase`. This could then be collapsed into a single QuerySet using Q objects.
But perhaps this is too complicated. Any comments welcomed.
"""