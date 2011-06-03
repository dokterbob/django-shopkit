Getting started
===============


#) Install the app basic_webshop in your environment using `PIP <http://pypi.python.org/pypi/pip/>`_  
   (better make sure you're working in a virtual environment):: 

    pip install -e git://salmon.dokterbob.net/basic-webshop.git#egg=basic-webshop

#) Enable the `basic_webshop` application in `INSTALLED_APPS` in `settings.py`::

    INSTALLED_APPS = (
        ...
        'shopkit.extensions.currency.simple',
        'basic_webshop',
        ...
    )

#) Import the webshop settings from `basic_webshop` in `settings.py`::

    from basic_webshop.django_settings import *

   Or add the settings manually::

    SHOPKIT_CUSTOMER_MODEL = 'basic_webshop.Customer'
    SHOPKIT_PRODUCT_MODEL = 'basic_webshop.Product'
    SHOPKIT_CART_MODEL = 'basic_webshop.Cart'
    SHOPKIT_CARTITEM_MODEL = 'basic_webshop.CartItem'
    SHOPKIT_ORDER_MODEL = 'basic_webshop.Order'
    SHOPKIT_ORDERITEM_MODEL = 'basic_webshop.OrderItem'
    SHOPKIT_CATEGORY_MODEL = 'basic_webshop.Category'


#) Now include the webshop URL's in `urls.py`::

    urlpatterns = patterns('',
        ...
        (r'^shop/', include('basic_webshop.urls')),
        ...
    )


#) Update the database by running `syncdb`::

    ./manage.py syncdb


#) You now have a working basic webshop, start developing in the `src`    
   directory in your environment. Make your own branch with::

    git checkout -b mywebshop

   And edit away! Whenever you want to update your own project with changes
   in the `basic_webshop` project, just do::

    git pull origin master
    git merge master


