basic_webshop
=============

A very basic webshop application based on the django-webshop framework. It
requires you to set the following settings::

    WEBSHOP_CUSTOMER_MODEL = 'basic_webshop.Customer'
    WEBSHOP_PRODUCT_MODEL = 'basic_webshop.Product'
    WEBSHOP_CART_MODEL = 'basic_webshop.Cart'
    WEBSHOP_ORDER_MODEL = 'basic_webshop.Order'
    WEBSHOP_CATEGORY_MODEL = 'basic_webshop.Category'


.. toctree::
   :maxdepth: 1

   models.rst
   views.rst

