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

import logging
logger = logging.getLogger(__name__)

from shopkit.core.utils import get_model_from_string

from shopkit.category.settings import CATEGORY_MODEL
category_class = get_model_from_string(CATEGORY_MODEL)


""" Mixins relevant for shops with categories. """

class CategoriesMixin(object):
    """ View Mixin providing a list of categories. """
    
    def get_context_data(self, **kwargs):
        """ Adds the available categories to the context as `categories`."""
        
        logger.debug(u'CategoriesMixin')

        context = super(CategoriesMixin, self).get_context_data(**kwargs)
        
        context.update({'categories': category_class.get_categories()})
        
        return context
