==============
django-webshop
==============

Webshop framework for Django
----------------------------
Similar to the way that Django is a web application framework, django-webshop
is a webshop application framework. It is, essentially, a toolkit for
building customized webshop applications, for 'perfectionists with deadlines'.

Getting started
---------------
Copy the example webshop app from `examples/basic_webshop` to wherever you
would like to work on your Django webshop app. Make sure you have installed
the django-webshop package and add the following applications to 
`INSTALLED_APPS` in `settings.py`::

    INSTALLED_APPS = (
        ...
        'webshop.core',
        'basic_webshop',
        ...
    )

Now include the webshop URL's in `urls.py`::

   urlpatterns = ...


