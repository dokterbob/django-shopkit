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

""" 
Images extension, allowing us to attach images to products using an
ImageField. It provides a `ProductImageBase` abstract base class and a setting
for defining the actual class implementing product images. This extension also
provides an AdminInline class for updating product images from within the
Admin interface and an Admin Mixin for showing thumbnails from within the
list view.

This extension is loosely coupled to the new 
`sorl-thumbnail <https://github.com/sorl/sorl-thumbnail>`_ - it will scale
thumbnails when Sorl is available but should work just fine without it.
"""