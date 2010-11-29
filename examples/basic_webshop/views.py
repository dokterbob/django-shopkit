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

from django.views.generic import DetailView, ListView, \
                                 TemplateView

from basic_webshop.models import Product, Category, Cart, CartItem


from webshop.core.views import CartAddFormMixin
from webshop.core.util import get_cart_from_request

from webshop.extensions.category.simple.views import CategoriesMixin


class WebshopViewMixin(CategoriesMixin):
    """ Generic view mixin, providing a shopping cart and categories
        as extra context. This Mixin should later be split up in
        several parts, some of which belong into the core and some of
        which will be part of extensions. 
        
        Class Based Views are Aweseome!
    
    """ 
    
    pass


class CategoryList(WebshopViewMixin, TemplateView):
    """ A dummy view taking the list of categories from the Mixin
        and displaying it using a simple template. """
    
    template_name = 'basic_webshop/category_list.html'


class CategoryDetail(WebshopViewMixin, DetailView):
    """ List products for a category. """
    
    model = Category
        

class ProductDetail(WebshopViewMixin, CartAddFormMixin, DetailView):
    """ List details for a product. """
    
    model = Product
    
    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        
        category = get_object_or_404(Category, slug=category_slug)
        
        queryset = Product.in_shop.all()
        return queryset.filter(category=category)


class CartDetail(WebshopViewMixin, TemplateView):
    """ A simple template view returning cart details,
        since the cart is already given in the template context from
        the WebshopViewMixin. """
    
    template_name = 'basic_webshop/cart_detail.html'


from django.contrib import messages

from django.views.generic.edit import BaseFormView
from django.core.urlresolvers import reverse

class CartAdd(CartAddFormMixin, BaseFormView):
    """ View for processing POST requests adding items to the shopping
        cart. Process flow is as follows:
        
        1. User is on a product detail page.
        2. User clicks 'Add to cart' and (optionally) selects a 
           quantity. This initiates a POST request to the current view.
        3. The current view fetches the cart, checks for the current
           product in there. 
        4. a) If it does, it adds the given quantity to
              CartItem which has been found.
           b) If it does not, a new CartItem should be created and added
              to the users Cart.
        5. Redirect to the cart view.
        
        """
    
    http_method_names = ['post', ]
    """ Only allow for post requests to this view. This is necessary to
        override the `get` method in BaseFormView. """

    def get_success_url(self):
        """ Get the URL to redirect to after a successful update of
            the shopping cart. This defaults to the shopping cart
            detail view. """
        
        return reverse('cart_detail')

    def get_form_class(self):
        """ Simply wrap the get_cart_form_class from CartMixin. """
        return self.get_cart_form_class()
        
    def form_valid(self, form):
        """ Form data was valid: add a CartItem to the Cart or increase
            the number. """
        
        cart = get_cart_from_request(self.request)

        # The cart might not have been saved so far
        if not cart.pk:
            cart.save()

        product = form.cleaned_data['product']
        quantity = form.cleaned_data['quantity']
        
        self.object = cart.addProduct(product, quantity)
        
        # Make sure that we know whether we updated an existing item
        updated = self.object.pk or False
        
        # After this, it will allways have a pk.
        self.object.save()
        
        if updated:
            # Object updated
            messages.add_message(self.request, messages.SUCCESS, 
                'Updated \'%s\' in shopping cart.' % product)
        else:
            # Object updated
            messages.add_message(self.request, messages.SUCCESS, 
                'Added \'%s\' to shopping cart.' % product)
        
        return super(BaseFormView, self).form_valid(form)


class ShopIndex(WebshopViewMixin, TemplateView):
    """ An index view for the shop, containing only the default context
        of the WebshopViewMixin. """
    
    template_name = 'basic_webshop/index.html'

