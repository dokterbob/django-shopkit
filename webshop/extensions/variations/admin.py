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

from django.contrib import admin

from webshop.extensions.variations.settings import PRODUCTVARIATION_MODEL
from webshop.core.util import get_model_from_string
productvariation_class = get_model_from_string(PRODUCTVARIATION_MODEL)


class ProductVariationInline(admin.TabularInline):
    """ Inline admin for product variations. """

    model = productvariation_class
    extra = 1


class VariationInlineMixin(object):
    """
    Base class for Admin Inline's (such as prices) in which we should be able
    to select Variations only pertaining to a specific Product.
    """

    def get_formset(self, request, obj=None, **kwargs):
        """
        Make sure we can only select variations that relate to the current
        product.

        This should be part of the django-webshop variations extension.
        TODO: Unittest this mother...

        Reference: http://stackoverflow.com/questions/1824267/limit-foreign-key-choices-in-select-in-an-inline-form-in-admin

        """
        formset = super(VariationInlineMixin, self).get_formset(request, obj=None, **kwargs)

        if obj and formset.form.base_fields.has_key('variation'):
            formset.form.base_fields['variation'].queryset = \
                formset.form.base_fields['variation'].queryset.filter(product=obj)

        return formset

