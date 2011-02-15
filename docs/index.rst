.. django-webshop documentation master file, created by
   sphinx-quickstart on Sat Nov  6 13:12:00 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to django-webshop's documentation!
==========================================

Webshop framework for Django
----------------------------
Similar to the way that Django is a web application framework, django-webshop
is a webshop application framework. It is, essentially, a toolkit for
building customized webshop applications, for 'perfectionists with deadlines'.

Compatibility
-------------
This piece of software will be compatible with Django 1.3. Due to the 
unavailability of Class Based Generic Views, it will not work on earlier
releases. It is being developed on the SVN trunk until Django hits the 1.3
release.

Dependencies
------------
You will need the dependencies mentioned in `requirements.txt` to be installed
somewhere in your `PYTHONPATH`. `django-webshop` will default to using (the
new) `sorl-thumbnail <https://github.com/sorl/sorl-thumbnail>`_ when
available, but does not depend on it.

When available, it has support for MPTT indexing of nested categories using
`django-mptt <https://github.com/django-mptt/django-mptt>`_. However, this
support is entirely optional, though using  some kind of tree optimization
algorithm is recommended.

Contents
--------

.. toctree::
   :maxdepth: 2

   gettingstarted.rst 
   
   todo.rst

   extending.rst

   components/index.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Last update: |today|

