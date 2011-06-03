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

from django.forms.models import BaseInlineFormSet
from django import forms


class PriceInlineFormSet(BaseInlineFormSet):
    """ Formset which makes sure that at least one price is filled in. """
    
    def clean(self):
        """ Raise a ValidationError if no Price forms are filled in. """
        
        # Raise this error when no forms exist or when no price has been 
        # specified in the first form.
        if len(self.forms) < 1 or \
            (not any(self.forms[0].errors) and \
             not self.forms[0].cleaned_data.has_key('price')):
            raise forms.ValidationError(
                _('At least one price should be provided.'))
