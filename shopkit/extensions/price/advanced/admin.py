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

from django.contrib import admin

from shopkit.core.utils import get_model_from_string

from shopkit.extensions.price.advanced.forms import PriceInlineFormSet
from shopkit.extensions.price.advanced.settings import PRICE_MODEL
price_class = get_model_from_string(PRICE_MODEL)


class PriceInline(admin.TabularInline):
    """ Inline price admin for prices belonging to products. """
    
    model = price_class
    
    extra = 1
    """ By default, onlye one extra form is shown, as to prevent clogging up
        of the user interface.
    """
    
    formset = PriceInlineFormSet
    """ An alias for :class:`PriceInlineFormSet <shopkit.extensions.price.advanced.forms.PriceInlineFormSet>`."""
