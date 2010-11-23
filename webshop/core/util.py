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

from django.db.models import get_model

""" Several util functions for use in core functionality. """

def get_model_from_string(model):
    """ 
    Takes a string in the form of `appname.Model`, (ie.
    `basic_webshop.CartItem`) and returns the model class for it.
    """
    
    return get_model(*model.split('.'))
