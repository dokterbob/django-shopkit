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

from django.db import models
from django.utils.translation import ugettext_lazy as _

from shopkit.related.settings import RELATED_SYMMETRICAL


class RelatedProductsMixin(models.Model):
    """ Mixin to allow for relating products to one another. """

    class Meta:
        abstract = True

    related = models.ManyToManyField('self', null=True, blank=True,
                                     symmetrical=RELATED_SYMMETRICAL,
                                     verbose_name=_('related products'))
