Components
==========

It is of the *utmost* importance to keep core and extension functionality
separated.

The criterium for this should be in the dependency tree of the respective
modules: core modules should *never* depend on extension modules but are free
to depend on one another. Similarly: extensions modules can freely depend on
any core modules but should, generally, not depend on one another.

Furthermore: the core API should provide for hooks to allow for any of the
extension modules. Hooks should be added only when an actual need for them
exist and not beforehand, as we should keep the code, API and documentation as
simple as possible.

Contents:

.. toctree::
   :maxdepth: 2

   core/index.rst
   price/index.rst
   shipping/index.rst
   category/index.rst
   vat/index.rst
   currency/index.rst
   configurable/index.rst
   variations/index.rst
   images/index.rst
   discounts/index.rst
   stock/index.rst
   related/index.rst
   brands/index.rst
   featured/index.rst

