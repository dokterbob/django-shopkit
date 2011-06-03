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

from django.db import models

from webshop.extensions.category.settings import *
from webshop.extensions.category.basemodels import *


class CategorizedItemBase(models.Model):
    """ Advanced base class for a simple categorized item, 
        belonging to only once single category. """
    
    class Meta:
        abstract = True
    
    category = models.ForeignKey(CATEGORY_MODEL)
    """ Category for the current product. """
