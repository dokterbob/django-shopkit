# Copyright (C) 2010-2011 Mathijs de Bruin <mathijs@mathijsfietst.nl>
#
# This file is part of django-webshop.
#
# django-webshop is free software; you can redistribute it and/or modify
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

from django.utils.decorators import classonlymethod
from django.utils.functional import update_wrapper


class Listener(object):
    """
    Class-based listeners, based on Django's class-based generic views. Yay!

    Usage::

        class MySillyListener(Listener):
            def dispatch(self, sender, **kwargs):
                # DO SOMETHING
                pass

        funkysignal.connect(MySillyListener.as_view(), weak=False)
    """

    def __init__(self, **kwargs):
        """
        Constructor. Called in the URLconf; can contain helpful extra
        keyword arguments, and other things.
        """
        # Go through keyword arguments, and either save their values to our
        # instance, or raise an error.
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    @classonlymethod
    def as_listener(cls, **initkwargs):
        """
        Main entry point for a sender-listener process.
        """
        # sanitize keyword arguments
        for key in initkwargs:
            if key in cls.http_method_names:
                raise TypeError(u"You tried to pass in the %s method name as a "
                                u"keyword argument to %s(). Don't do that."
                                % (key, cls.__name__))
            if not hasattr(cls, key):
                raise TypeError(u"%s() received an invalid keyword %r" % (
                    cls.__name__, key))

        def listener(sender, **kwargs):
            self = cls(**initkwargs)
            return self.dispatch(sender, **kwargs)

        # take name and docstring from class
        update_wrapper(listener, cls, updated=())

        # and possible attributes set by decorators
        update_wrapper(listener, cls.dispatch, assigned=())
        return listener

    def dispatch(self, sender, **kwargs):
        raise NotImplementedError('Sublcasses should implement this!')
