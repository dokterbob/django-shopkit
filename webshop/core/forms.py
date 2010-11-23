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

from django import forms

from webshop.core.util import get_model_from_string
from webshop.core.settings import PRODUCT_MODEL


from django.utils.functional import SimpleLazyObject


def get_product_choices():
    """ Get available products for shopping cart. This
        has to be wrapped in a SimpleLazyObject, otherwise
        Sphinx will complain in the worst ways. """
    product_class = get_model_from_string(PRODUCT_MODEL)
    
    return product_class.in_shop.all()

product_choices = SimpleLazyObject(get_product_choices)


""" Core form classes. """

class CartItemAddForm(forms.Form):
    """ A form for adding CartItems to a Cart. """
    
    product = forms.ModelChoiceField(queryset=product_choices,
                                     widget=forms.HiddenInput)
    quantity = forms.IntegerField(min_value=1, initial=1)