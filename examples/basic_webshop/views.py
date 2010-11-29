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
logger = logging.getLogger('basic_webshop')


from django.shortcuts import get_object_or_404

from django.core.urlresolvers import reverse

from django.views.generic import DetailView, ListView, \
                                 TemplateView

from basic_webshop.models import Product, Category, Cart, CartItem


from webshop.core.views import CartAddFormMixin, CartAddBase


class CategoryList(TemplateView):
    """ A dummy view taking the list of categories from the Mixin
        and displaying it using a simple template. """
    
    template_name = 'basic_webshop/category_list.html'


class CategoryDetail(DetailView):
    """ List products for a category. """
    
    model = Category


class CartAdd(CartAddBase):
    """ View for adding a quantity of products to the cart. """
    
    def get_success_url(self):
        """ Get the URL to redirect to after a successful update of
            the shopping cart. This defaults to the shopping cart
            detail view. """
        
        return reverse('cart_detail')


class ProductDetail(CartAddFormMixin, DetailView):
    """ List details for a product. """
    
    model = Product
    
    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        
        category = get_object_or_404(Category, slug=category_slug)
        
        queryset = Product.in_shop.all()
        return queryset.filter(category=category)


from django.forms.models import modelformset_factory

from webshop.core.util import get_cart_from_request
from django.views.generic.edit import BaseFormView


class CartEditFormMixin(object):
    """ Mixin providing a formset for updating the quantities of
        products in the shopping cart. """
    
    def get_form_class(self):
        """ Do a little trick and see whether it works: returning a 
            formset instead of a form here.
        """
        formset_class =  modelformset_factory(CartItem, 
                                              exclude=('cart', 'product'),
                                              extra=0)
        
        return formset_class
    
    
    def get_form(self, form_class):
        """ Gets an instance of the formset. """
        cart = get_cart_from_request(self.request)
        
        qs = CartItem.objects.filter(cart=cart, quantity__gte=1)
                
        formset = form_class(queryset=qs)
        
        return formset

        
    def get_context_data(self, **kwargs):
        """ Add a form for editing the quantities of articles to 
            the template. """            
        
        context = super(CartEditFormMixin, self).get_context_data(**kwargs)
        
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context.update({'carteditformset': form})
        
        
        return context


class CartDetail(CartEditFormMixin, TemplateView):
    """ A simple template view returning cart details,
        since the cart is already given in the template context from
        the WebshopViewMixin. """
    
    template_name = 'basic_webshop/cart_detail.html'
    

class CartEdit(CartDetail, BaseFormView):
    """ View for updating the quantities of objects in the shopping 
        cart. """

    http_method_names = ['post', ]
    """ Only allow for post requests to this view. This is necessary to
        override the `get` method in BaseFormView. """

    def get_success_url(self):
        """ The URL to return to after the form was processed 
            succesfully. This function should be overridden. """
        
        # TODO
        # Decide whether or not to make the default success url a
        # configuration value or not.
        #raise NotImplemented

        return reverse('cart_detail')
    
    def form_valid(self, form):
        """ Save the formset. """
        
        pass






class ShopIndex(TemplateView):
    """ An index view for the shop, containing only the default context
        of the WebshopViewMixin. """
    
    template_name = 'basic_webshop/index.html'

