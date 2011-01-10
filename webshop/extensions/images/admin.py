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

import logging

logger = logging.getLogger(__name__)

from django.contrib import admin

from django.utils.translation import ugettext_lazy as _

from webshop.extensions.images.settings import PRODUCTIMAGE_MODEL
from webshop.core.util import get_model_from_string
productimage_class = get_model_from_string(PRODUCTIMAGE_MODEL)


class ProductImageInline(admin.TabularInline):
    """ Inline admin for product images. """
    
    model = productimage_class
    extra = 1


class ImagesProductMixin(object):
    """ 
    Mixin class adding a function for easily displaying images in the 
    product list display of the admin. To use this, simply add 
    `'default_image'` to the `list_display` tuple.
    
    Like such::
       ProductAdmin(<Base classes>, ImagesProductMixin):
          list_display = ('name', 'default_image')
    
    """
    
    def default_image(self, obj):
        """ Renders the default image for display in the admin list. """
        
        image = obj.get_default_image().image

        if image:
            return u'<a href="%d/"><img src="%s" alt="%s"/></a>' % \
                (obj.pk, image.url, unicode(obj))
        else:
            
            # TODO: return the path to a stub image
            return u''
    default_image.short_description = _('image')
    default_image.allow_tags = True


