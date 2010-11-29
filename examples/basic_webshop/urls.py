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

from surlex.dj import surl

from django.conf.urls.defaults import *

from basic_webshop.views import *

urlpatterns = patterns('',
    surl(r'^$',
         ShopIndex.as_view(), name='shop_index'),

    surl(r'^categories/$',
         CategoryList.as_view(), name='category_list'),
    surl(r'^categories/<slug:s>/$',
         CategoryDetail.as_view(), name='category_detail'),
    surl(r'^categories/<category_slug:s>/product/<slug:s>/$',
         ProductDetail.as_view(), name='product_detail'),
    
    surl(r'^cart/$',
         CartDetail.as_view(), name='cart_detail'),
    surl(r'^cart/add/$', CartAdd.as_view(), name='cart_add'),
    surl(r'^cart/edit/$', CartEdit.as_view(), name='cart_edit'),

)