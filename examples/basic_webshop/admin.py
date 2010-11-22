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

from basic_webshop.models import *


class ProductAdmin(admin.ModelAdmin):
    """ Model admin for products. """
    
    fields = ('name', 'slug', 'category', 'price', 'description')
    prepopulated_fields = {"slug": ("name",)}

    
admin.site.register(Product, ProductAdmin)


class CategoryAdmin(admin.ModelAdmin):
    """ Model admin for categories. """

    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Category, CategoryAdmin)
