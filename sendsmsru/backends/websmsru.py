#-*- coding: UTF-8 -*-
import ConfigParser
import logging
import urllib
import urllib2

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.encoding import smart_str

from sendsms.backends.base import BaseSmsBackend

logger = logging.getLogger(__name__)

WEBSMSRU_SMTP_EMAIL = 'post@websms.ru'
WEBSMSRU_HTTP_URL = 'http://websms.ru/http_in5.asp'

WEBSMSRU_USERNAME = settings.WEBSMSRU_USERNAME
WEBSMSRU_PASSWORD = settings.WEBSMSRU_PASSWORD


class SMTPClient(BaseSmsBackend):
    def format_phone(self, phone):
        return phone.lstrip('+')

    def send_messages(self, messages):

        result = 0
        for message in messages:
            context = dict(user=WEBSMSRU_USERNAME,
                           password=WEBSMSRU_PASSWORD,
                           from_phone=self.format_phone(message.from_phone),
                           tels=','.join(self.format_phone(tel)
                                         for tel in message.to),
                           mess=message.body)
            body = \
u"""user={user}
pass={password}
fromPhone={from_phone}
tels={tels}
mess={mess}
""".format(**context)
            msg = EmailMessage(subject=u'Send sms: %s' % message.body,
                               body=body,
                               to=[self.format_phone(WEBSMSRU_SMTP_EMAIL)])

            result += msg.send(fail_silently=self.fail_silently)

        return result


# based on https://github.com/mediasite/smsgate/blob/master/smsgate/gates/websms.py                       
class HTTPClient(BaseSmsBackend):

    common = dict(http_username=WEBSMSRU_USERNAME,
                  http_password=WEBSMSRU_PASSWORD)

    def _send(self, message):
        context = {
            'message': smart_str(message.body, encoding='cp1251'),
            'phone_list': ','.join(message.to),
            'fromPhone': smart_str(message.from_phone,
                                   encoding='ascii', errors='ignore'),
        }

        context.update(self.common)

        params = urllib.urlencode(context)
        try:
            resp = urllib2.urlopen('%s?%s' % (WEBSMSRU_HTTP_URL, params,))
        except IOError, exc:
            if not self.fail_silently:
                raise
            else:
                logger.error(u'Error sending: %s' % unicode(exc))
                return False

        resp_cp = ConfigParser.RawConfigParser()
        try:
            resp_cp.readfp(resp)
        except ConfigParser.Error:
            if not self.fail_silently:
                raise
            else:
                logger.error(u'Error sending: %s' % resp_cp.read())
                return False
 
        status = resp_cp.get('Common', 'error_num')
        if status != 'OK':
            errortext = 'Error sending: %s' % status.decode('cp1251')
            if not self.fail_silently:
                raise Exception(errortext)
            else:
                logger.exception(errortext)
                return False
        logger.debug(u'sms sended %s' % message.body)
        return True

    def send_messages(self, messages):
        result = 0
        for message in messages:
            result += self._send(message)
        return result


class SMPPClient(BaseSmsBackend):
    pass  # TODO
