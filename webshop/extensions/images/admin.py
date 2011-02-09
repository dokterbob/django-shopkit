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

try:
    from sorl.thumbnail.admin import AdminInlineImageMixin

    from sorl.thumbnail.default import backend as sorl_backend

    SORL_THUMBNAIL = True
    logger.debug('Sorl-thumbnail found: using it.')

except ImportError:
    class AdminInlineImageMixin(object):
        pass

    SORL_THUMBNAIL = False
    logger.debug('Sorl-thumbnail not found. Skipping.')


class ProductImageInline(AdminInlineImageMixin, admin.TabularInline):
    """ Inline admin for product images. """

    model = productimage_class
    extra = 1


class ImagesProductAdminMixin(object):
    """
    Mixin class adding a function for easily displaying images in the
    product list display of the admin. To use this, simply add
    `'default_image'` to the `list_display` tuple.

    Like such::

       ProductAdmin(ImagesProductAdminMixin, <Base classes>):
          list_display = ('name', 'default_image')

    """

    thumbnail_geometry = '150x150'

    def default_image(self, obj):
        """ Renders the default image for display in the admin list.
            Makes a thumbnail if `sorl-thumbnail` is available.

            .. todo::
                Add a setting for returning stub images when no
                default image currently exists.

        """

        image = obj.get_default_image()

        if image:
            if SORL_THUMBNAIL:
                # This should not raise an error when an image is non-
                # existant or something like that.
                try:
                    image = sorl_backend.get_thumbnail(image.image,
                                                       self.thumbnail_geometry)
                except:
                    logger.warn('Error rendering thumbnail')

            return u'<a href="%d/"><img src="%s" alt="%s"/></a>' % \
                (obj.pk, image.url, unicode(obj))
        else:

            return u''
    default_image.short_description = _('image')
    default_image.allow_tags = True


