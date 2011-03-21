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

from django.dispatch import Signal

order_state_change = Signal()
""" 
Signal called whenever an order changes from one state to another.

Listeners should have the following signature::

    def mylistener(sender, old_state, new_state, state_change, **kwargs):
        ...


:param sender: `Order` object
:param old_state: (raw value) of old state
:param new_state: (raw value) of new state
:param state_change: `OrderStateChange` pertaining to the state change
"""
