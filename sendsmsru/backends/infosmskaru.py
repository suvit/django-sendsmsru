#-*- coding: UTF-8 -*-
import logging
import urllib
import urllib2

from django.conf import settings
from django.utils.encoding import smart_str

from sendsms.backends.base import BaseSmsBackend

logger = logging.getLogger(__name__)

HTTP_URL = 'http://api.infosmska.ru/interfaces/SendMessages.ashx'

USERNAME = settings.INFOSMSKARU_USERNAME
PASSWORD = settings.INFOSMSKARU_PASSWORD


class HTTPClient(BaseSmsBackend):

    common = dict(login=USERNAME,
                  pwd=PASSWORD)


    def format_phone(self, phone):
        return phone.lstrip('+')

    def send_messages(self, messages):
        result = 0
        for message in messages:
            result += self._send(message)
        return result

    def _send(self, message):
        context = {
            'message': smart_str(message.body, encoding='utf8'),
            'phones': ','.join(self.format_phone(tel)
                               for tel in message.to),
            'sender': smart_str(message.from_phone,
                                encoding='ascii', errors='ignore'),
        }

        context.update(self.common)

        params = urllib.urlencode(context)
        try:
            resp = urllib2.urlopen('%s?%s' % (HTTP_URL, params,))
        except IOError, exc:
            if not self.fail_silently:
                raise
            else:
                logger.error(u'Error sending: %s' % unicode(exc))
                return False

        resp = resp.read()
        logger.debug('response was %s' % resp)
        if not resp.startswith('Ok:'):
            if not self.fail_silently:
                raise RuntimeError(resp)
            else:
                logger.error(u'Error sending: %s' % repr(resp))
                return False

        logger.debug(u'sms sended %s' % smart_str(message.body, encoding='utf8'))
        return True


class SOAPClient(BaseSmsBackend):
    pass # TODO
