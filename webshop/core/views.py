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

from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import BaseFormView

from django.contrib import messages

from django.utils.translation import ugettext_lazy as _

from webshop.core.utils import get_model_from_string

from webshop.core.settings import CART_MODEL
from webshop.core.forms import CartItemAddForm


""" Generic view Mixins for webshop core functionality. """


class InShopViewMixin(object):
    """
    Mixin using the `in_shop` manager rather than the default `objects`,
    so that it only uses objects which are actually enabled in the frontend of
    the shop.
    """

    def get_queryset(self):
        """ Return `in_shop.all()` for the `model`. """
        return self.model.in_shop.all()


class CartAddFormMixin(object):
    """ Mixin providing a basic form class for adding items to the
        shopping cart. It will be added to the context as `cartaddform`.
    """

    def get_cart_form_class(self):
        """ Simply return the form for adding Items to a Cart. """

        return CartItemAddForm


    def get_context_data(self, **kwargs):
        """
        Add a cart add form under the name `cartaddform` to the
        context, if and only if an object is available and is a product.

        If this is not the case, we should fail silently (perhaps)
        logging a debug message.

        .. todo::
            Make an API hook allowing us to check whether a product available
            for adding it to a cart.

        """

        cartform_class = self.get_cart_form_class()

        cartform = cartform_class(initial={'product':self.object})

        context = super(CartAddFormMixin, self).get_context_data(**kwargs)

        context.update({'cartaddform': cartform})

        return context


class CartAddBase(TemplateResponseMixin, CartAddFormMixin, BaseFormView):
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

        .. todo::
            Graceously handle errors instead of form_invalid noting that
            render_to_response was not found.

        """

    http_method_names = ['post', ]
    """ Only allow for post requests to this view. This is necessary to
        override the `get` method in BaseFormView. """

    def get_success_url(self):
        """
        The URL to return to after the form was processed
        succesfully. This function should be overridden.

        .. todo::
            Decide whether or not to make the default success url a
            configuration value or not.

        """

        raise NotImplemented

    def get_form_class(self):
        """ Simply wrap the get_cart_form_class from CartMixin. """
        return self.get_cart_form_class()

    def form_valid(self, form):
        """
        Form data was valid: add a CartItem to the Cart or increase
        the number.

        ..todo::
            Refactor this!
        """

        cart = get_cart_from_request(self.request)

        # The cart might not have been saved so far
        if not cart.pk:
            cart.save()

        product = form.cleaned_data['product']
        quantity = form.cleaned_data['quantity']

        self.object = cart.add_item(product, quantity)

        # Make sure that we know whether we updated an existing item
        updated = self.object.pk or False

        # After this, it will allways have a pk.
        self.object.save()

        if updated:
            # Object updated
            messages.add_message(self.request, messages.SUCCESS,
                _('Updated \'%s\' in shopping cart.') % product)
        else:
            # Object updated
            messages.add_message(self.request, messages.SUCCESS,
                _('Added \'%s\' to shopping cart.') % product)

        return super(BaseFormView, self).form_valid(form)


