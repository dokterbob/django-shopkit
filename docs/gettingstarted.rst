Getting started
===============

Copy the example webshop app from `examples/basic_webshop` to wherever you
would like to work on your Django webshop app. We will assume you have named
it `mywebshop`, below. Make sure you have installed the django-webshop
package into your Python path and add the following applications to
`INSTALLED_APPS` in `settings.py`::

    INSTALLED_APPS = (
        ...
        'mywebshop',
        ...
    )

Now include the webshop URL's in `urls.py`::

    urlpatterns = patterns('',
        ...
        (r'^shop/', include('mywebshop.urls')),
        ...
    )


And add the required settings::

    WEBSHOP_PRODUCT_MODEL = 'mywebshop.Product'
    WEBSHOP_CART_MODEL = 'mywebshop.Cart'
    WEBSHOP_ORDER_MODEL = 'mywebshop.Order'
    WEBSHOP_CATEGORY_MODEL = 'mywebshop.Category'
