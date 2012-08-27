#-*- coding: UTF-8 -*-
import ConfigParser
import urllib
import urllib2

from django.conf import settings
from django.core.mail import EmailMessage

from sendsms.backends.base import BaseSmsBackend

WEBSMSRU_SMTP_EMAIL = 'post@websms.ru'
WEBSMSRU_HTTP_URL = 'http://websms.ru/http_in5.asp'

WEBSMSRU_USERNAME = settings.WEBSMSRU_USERNAME
WEBSMSRU_PASSWORD = settings.WEBSMSRU_PASSWORD

class SMTPClient(BaseSmsBackend):
    def send_messages(self, messages):
        result = 0
        for message in messages:
            context = dict(user=WEBSMSRU_USERNAME,
                           pass=WEBSMSRU_PASSWORD,
                           from=message.from_phone,
                           tels=','.join(message.to),
                           mess=message.body)
            body = u"""
user={user}
pass={pass}
fromPhone={from}
tels={tels}
mess={mess}
""".format(context)
            msg = EmailMessage(subject=u'Send sms: %s' % message.body,
                               body=body,
                               to=WEBSMSRU_SMTP_EMAIL)

            result += msg.send(fail_silently=self.fail_silently)

        return result

# based on https://github.com/mediasite/smsgate/blob/master/smsgate/gates/websms.py                       
class HTTPClient(BaseSmsBackend):

    common = dict(http_username=WEBSMSRU_USERNAME,
                  http_password=WEBSMSRU_PASSWORD)

    def _send(self, message):
        for to in message.to:
            d = {
                'message': message.body,
                'phone_list': to,
                'packet_id': hash(self),
                'fromPhone']: message.from_phone,
            }

            d.update(self.common)
            params = urllib.urlencode(d)

            resp = urllib2.urlopen('%s?%s' % (SEND_ADDR, params,))
            resp_cp = ConfigParser.RawConfigParser()
            resp_cp.readfp(resp)

            status = resp_cp.get('Common', 'error_num')
            if status != 'OK':
                errortext = 'Error sending: %s' % status
                if not self.fail_silently:
                    raise Exception(errortext)
                else:
                    logger.error(errortext)
                    return False
        return True

    def send_messages(self, messages):
        result = 0
        for message in messages:
            result += self._send(message)
        return result
