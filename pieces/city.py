# coding=utf-8
import json
import urllib2
from urllib import urlencode

from django.conf import settings

from mobile.models.constants import HTTP_TIMEOUT, PROVINCES


def get_ip_city(ip):
    ''' According to the ip, get the request user's city.'''

    url = 'http://int.dpool.sina.com.cn/iplookup/iplookup.php'
    url = getattr(settings, 'GET_CITY_API_URL', url)
    data = {
        'format': 'json',
        'ip': ip,
    }
    addr = {
        'country': u'中国',
        'province': u'北京',
        'city': u'北京',
        'near_city': u'北京',
        'is_china': True
    }
    req = urllib2.Request('%s?%s' % (url, urlencode(data)))
    try:
        res = urllib2.urlopen(req, timeout=HTTP_TIMEOUT).read()
        ret = json.loads(res)
        if (ret['ret'] > 0) and (ret['country'] == u'中国'):
            addr.update({
                'country': ret['country'],
                'province': ret['province'],
                'city': ret['city'],
                'is_china': True
            })
    except:
        pass
    else:
        if not addr['city']:
            if addr['province'] and (addr['province'] in PROVINCES):
                addr.update({
                    'city': PROVINCES[addr['province']],
                    'near_city': PROVINCES[addr['province']]
                })
            else:
                addr.update({
                    'city': u'北京',
                    'is_china': True
                })
        else:
            if addr['province'] and (addr['province'] in PROVINCES):
                addr.update({
                    'near_city': PROVINCES[addr['province']]
                })
            else:
                addr.update({
                    'near_city': u'北京'
                })

    return addr
