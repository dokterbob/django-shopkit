Writing extensions
==================

Extension practises
-------------------

In order to provide for extensionability, two different mechanism can be
applied:

1. Whenever it makes sense to have only one extension module activated at the
same time, we should opt for a combination of subclassing :ref:`abstract base classes <abstract-base-classes>`
and explicitly refererring to these classes from `settings.py`. This mechanism
is to be used for things like products, categories, orders and shopping carts.
In some situations we might want to default to a builtin implementation of the
abstract base class.

2. For other functionality, such as taxes, shipment, payment or stock
management we want to allow for a mechanism similar to the way the :class:`Django admin <django.contrib.admin.ModelAdmin>`  is extended, using a combination of subclassing and explicit registration of
plugin modules.

These approaches have the added advantage that it does not matter where in the
module tree extensions are located. They might are will often reside in
different packages or applications, which may not pose a problem in any way.