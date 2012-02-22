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

from django.utils.translation import ugettext_lazy as _
from django.db import models

from shopkit.category.settings import CATEGORY_MODEL
from shopkit.category.settings import USE_MPTT


class CategoryBase(models.Model):
    """ Abstract base class for a category. """

    class Meta:
        abstract = True
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    objects = models.Manager()
    in_shop = objects
    """ The `in_shop` property should be a :class:`Manager <django.db.models.Manager>`
        containing all the items which should be enabled in the
        shop's frontend.
    """

    @classmethod
    def get_categories(cls):
        """ Gets all the available categories. """

        return cls.in_shop.all()


    @classmethod
    def get_main_categories(cls):
        """
        Gets the main categories, which for unnested categories
        implies all of them. This method exists purely for uniformity
        reasons.
        """

        categories = cls.get_categories()

        return categories


    def get_products(self):
        """ Get all active products for the current category.
        """

        from shopkit.core.settings import PRODUCT_MODEL
        from shopkit.core.utils import get_model_from_string
        product_class = get_model_from_string(PRODUCT_MODEL)

        return product_class.in_shop.filter(category=self)


class NestedCategoryBase(CategoryBase):
    """
    Abstract base class for a nested category.
    """

    class Meta(CategoryBase.Meta):
        abstract = True

    parent = models.ForeignKey(CATEGORY_MODEL, null=True, blank=True,
                               verbose_name=_('parent category'),
                               help_text=_('If left empty, this will be a \
                                            main category.'))
    """ Parent of this category """

    @classmethod
    def get_main_categories(cls):
        """ Gets the main categories; the ones which have no parent. """

        categories = super(NestedCategoryBase, cls).get_main_categories()

        return categories.filter(parent__isnull=True)

    def get_subcategories(self):
        """ Gets the subcategories for the current category. """

        categories = self.get_categories()

        return categories.filter(parent=self)

    def get_products(self):
        """ Get all active products for the current category.

            For performance reasons, and added control, this only
            returns only products explicitly associated to this
            category - as opposed to listing also products in subcategories
            of the current category.

            This would take a lot more requests and is probably not
            what we should wish for.
        """

        from shopkit.core.settings import PRODUCT_MODEL
        from shopkit.core.utils import get_model_from_string
        product_class = get_model_from_string(PRODUCT_MODEL)

        return product_class.in_shop.filter(categories__in=self)

    def get_parent_list(self, reversed=False):
        """ Return a list of all parent categories of the current category.

            By default it lists the categories from parent to child, ie.::

                [<categoryt>, <subcategory>, <subsubcategory>, ...]

            If the argument `reversed` evaluates to `True`, the list runs
            in reverse order. This *saves* an extra reverse operation.

            .. todo::
                Cache this. It is a slow operation which requires
                as many queries as the category tree is deep.
        """

        current = self
        parent_list = []
        while current.parent:
            parent_list.append(current.parent)
            current = current.parent

        if not reversed:
            parent_list.reverse()

        return parent_list


    def __unicode__(self):
        """ The unicode representation of a nested category is that of
            it's parents and the current, separated by two colons.

            So something like: <main> :: <sub> :: <subsub>
        """


        parent_list = self.get_parent_list()
        result_list = []
        for parent in parent_list:
            super_unicode = super(NestedCategoryBase, parent).__unicode__()
            result_list.append(super_unicode)

        super_unicode = super(NestedCategoryBase, self).__unicode__()

        result_list.append(super_unicode)

        result = ' :: '.join(result_list)

        return result

"""
:class:MPTTCategoryBase
Blabla
"""
if USE_MPTT:
    logger.debug(u'Enabling MPTTCategoryBase with category tree optimalization')

    from mptt.models import MPTTModel
    from mptt.managers import TreeManager

    class MPTTCategoryBase(MPTTModel, NestedCategoryBase):
        tree = TreeManager()

        class Meta(MPTTModel.Meta, NestedCategoryBase.Meta):
            abstract = True

        @classmethod
        def get_main_categories(cls):
            """ Gets the main categories; the ones which have no parent. """

            return cls.tree.root_nodes()

        def get_subcategories(self):
            """ Gets the subcategories for the current category. """

            return self.get_children()

        def get_products(self):
            """
            Get all active products for the current category.

            As opposed to the original function in the base class, this also
            includes products in subcategories of the current category object.

            """

            from shopkit.core.settings import PRODUCT_MODEL
            from shopkit.core.utils import get_model_from_string
            product_class = get_model_from_string(PRODUCT_MODEL)

            in_shop = product_class.in_shop
            descendants = self.get_descendants(include_self=True)

            return in_shop.filter(categories__in=descendants).distinct()

        def __unicode__(self):
            """ The unicode representation of a nested category is that of
                it's parents and the current, separated by two colons.

                So something like: <main> :: <sub> :: <subsub>

                ..todo::
                    Make some kind of cache on the model to handle repeated
                    queries of the __unicode__ value without extra queries.
            """

            parent_list = self.get_ancestors()
            result_list = []
            for parent in parent_list:
                super_unicode = super(NestedCategoryBase, parent).__unicode__()
                result_list.append(super_unicode)

            super_unicode = super(NestedCategoryBase, self).__unicode__()

            result_list.append(super_unicode)

            result = ' :: '.join(result_list)

            return result

else:
    logger.debug(u'Not using mptt for nested categories: not in INSTALLED_APPS')


