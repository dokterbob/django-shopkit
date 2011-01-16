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

from django.test import TestCase
from django.conf import settings

from webshop.core.util import get_model_from_string


class CategoryTestMixinBase(object):
    """
    Base class for testing categories.
    """
    
    def setUp(self):
        """
        We want to have the category class available in `self`.
        """
        
        super(CategoryTestMixinBase, self).setUp()
        
        self.category_class = \
            get_model_from_string(settings.WEBSHOP_CATEGORY_MODEL)
        
    def make_test_category(self):
        """ 
        Abstract function for creating a test category. As the actual
        properties of Products depend on the classes actually implementing
        it, this function must be overridden in subclasses.
        """
        
        raise NotImplementedError
    
    def test_basic_category(self):
        """ Test if we can make and save a simple category. """
        
        c = self.make_test_category()
        c.save()
        
        self.assert_(c.pk)
