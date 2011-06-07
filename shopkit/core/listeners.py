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

from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMultiAlternatives

from django.template.loader import render_to_string
from django.contrib.sites.models import Site

from django.utils import translation

from shopkit.core.utils.listeners import Listener


class StateChangeListener(Listener):
    """
    Listener base class for order status changes.

    Example::

        OrderPaidListener(StatusChangeListener):
            state = order_states.ORDER_STATE_PAID

            def handler(self, sender, **kwargs):
                # <do something>
    """

    new_state = None
    old_state = None

    def dispatch(self, sender, **kwargs):
        """
        The dispatch method is equivlant to the similarly named method in
        Django's class based views: it checks whether or not this signal
        should be handled at all (whether or not it matches the specified)
        state change) and then calls the `handle()` method.
        """
        # Match the new state, if given
        if self.new_state and not self.new_state == sender.state:
            logger.debug(u'Signal for %s doesn\'t match listener for %s', sender, self)
            return

        # Match the old state
        if self.old_state and not self.old_state == kwargs['old_state']:
            logger.debug(u'Old state for %s doesn\'t match old state for listener %s', sender, self)
            return

        self.handler(sender, **kwargs)

    def handler(self, sender, **kwargs):
        """
        The handler performs some actual action upon handling a signal. This
        must be overridden in subclasses defining *actual* listeners.
        """
        raise NotImplementedError('Better give me some function to fulfill')


class StateChangeLogger(StateChangeListener):
    """
    Debugging listener for `order_state_change`,
    logging each and every state change.
    """

    def handler(self, sender, **kwargs):
        """ Handle the signal by writing out a debug log message. """
        old_state = kwargs['old_state']
        new_state = sender.state

        logger.debug(u'State change signal: from %s to %s for %s',
                     old_state, new_state, sender)


class EmailingListener(Listener):
    """ Listener which sends out emails. """

    body_template_name = None
    body_html_template_name = None
    subject_template_name = None

    def get_subject_template_names(self):
        """
        Returns a list of template names to be used for the request. Must
        return a list. May not be called if render_to_response is overridden.
        """
        if self.subject_template_name is None:
            raise ImproperlyConfigured(
                "TemplateResponseMixin requires either a definition of "
                "'template_name' or an implementation of 'get_template_names()'")
        else:
            return [self.subject_template_name]

    def get_body_template_names(self):
        """
        Returns a list of template names to be used for the request. Must
        return a list. May not be called if render_to_response is overridden.
        """
        if self.body_template_name is None:
            raise ImproperlyConfigured(
                "TemplateResponseMixin requires either a definition of "
                "'template_name' or an implementation of 'get_template_names()'")
        else:

            return [self.body_template_name]

    def get_body_html_template_names(self):
        """
        Returns a list of HTML template names to be used for the request. Must
        return a list. May not be called if render_to_response is overridden.
        """
        if self.body_html_template_name is None:
            return None
        else:
            return [self.body_html_template_name]

    def get_context_data(self):
        """
        Context for the message template rendered. Defaults to sender, the
        current site object and kwargs.
        """

        current_site = Site.objects.get_current()

        context = {'sender': self.sender,
                   'site': current_site}

        context.update(self.kwargs)

        return context

    def get_recipients(self):
        """ Get recipients for the message. """
        raise NotImplementedError

    def get_sender(self):
        """
        Sender of the message, defaults to `None` which imples
        `DEFAULT_FROM_EMAIL`.
        """
        return None

    def create_message(self, context):
        """ Create an email message. """
        recipients = self.get_recipients()
        sender = self.get_sender()

        subject = render_to_string(self.get_subject_template_names(), context)
        # Clean the subject a bit for common errors (newlines!)
        subject = subject.strip().replace('\n', ' ')

        body = render_to_string(self.get_body_template_names(), context)

        email = EmailMultiAlternatives(subject, body, sender, recipients)

        html_body_template_names = self.get_body_html_template_names()
        if html_body_template_names:
            html_body = render_to_string(html_body_template_names, context)
            email.attach_alternative(html_body, 'text/html')

        return email

    def handler(self, sender, **kwargs):
        """ Store sender and kwargs attributes on self. """

        self.sender = sender
        self.kwargs = kwargs

        context = self.get_context_data()

        message = self.create_message(context)

        message.send()


class TranslatedEmailingListener(EmailingListener):
    """ Email sending listener which switched locale before processing. """

    def get_language(self, sender, **kwargs):
        """ Return the language we should switch to. """
        raise NotImplementedError

    def handler(self, sender, **kwargs):
        """
        Handle the signal, wrapping the emailing handler from the base
        class but changing locale on beforehand, switching back to the
        original afterwards.
        """
        old_language = translation.get_language()

        language = self.get_language(sender, **kwargs)

        logger.debug('Changing to language %s for email submission', language)
        translation.activate(language)

        super(TranslatedEmailingListener, self).handler(sender, **kwargs)

        translation.activate(old_language)
