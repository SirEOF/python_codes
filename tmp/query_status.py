# coding:utf-8
import json
import logging

import os
from concurrent.futures import ThreadPoolExecutor

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gongpingjia.settings")
import django

django.setup()
import sys

parent = lambda path, count: \
    parent(os.path.dirname(path), count - 1) if count > 0 else path
sys.path.insert(0, parent(os.path.abspath(__file__), 3))

reload(sys)
sys.setdefaultencoding('utf8')
from django.db.models import Q
import hashlib
import requests
import time
from datetime import datetime
from datetime import timedelta
from django.db import close_old_connections

logger = logging.getLogger('status_query.errors')


def get_push_record(plate_form=None):
    exclude_status = ('F', 'Y', 'D', 'C')
    base_query = Q(status__in=exclude_status)
    if plate_form:
        close_old_connections()
        push_records = PushCarToCooperation.objects.using('master').filter(dealer_name=plate_form, create_time__gte=(
            datetime.now() - timedelta(days=30))).exclude(base_query).order_by('-id')
    else:
        push_records = PushCarToCooperation.objects.using('master').exclude(base_query).order_by('-id')
    return list(push_records)


def store_record(push_record, info):
    if not push_record.car_status.filter(status=info).exists():
        print push_record.id, info
        data = {
            'push_record': push_record,
            'status': info,
            'dealer_name': push_record.dealer_name,
            'index_id': push_record.index_id,
            'push_time': push_record.create_time,
            'car_id': push_record.trade_car.id,
            'car_meta_data': push_record.trade_car.meta_data,
            'car_source': push_record.trade_car.source,
            'car_create_time': push_record.trade_car.created_on,
            'car_badge_num': push_record.trade_car.badge_number,
            'car_server_time': push_record.trade_car.serve_on
        }
        close_old_connections()
        pcfb = PushCarFeedBack.objects.create(**data)
        print pcfb.id


class CooperationStatusQueryMixin():
    """ 平台查询mixin
    """
    status_query_url = ''

    @classmethod
    def _prepare_params(cls, obj):
        pass

    @classmethod
    def _query(cls, params):
        return None

    @classmethod
    def _resolve_resp(cls, response):
        return response

    @classmethod
    def _update_status(cls, resp, obj):
        pass

    @classmethod
    def query_status(cls, obj):
        try:
            params = cls._prepare_params(obj)
            resp = cls._query(params)
            resp_data = cls._resolve_resp(resp)
            cls._update_status(resp_data, obj)
        except Exception as e:
            logger.error(e.message)

    @classmethod
    def get_multi(cls, *args, **kws):
        return []

    @classmethod
    def bunch_query(cls, max_workers=48, *args, **kws):
        multi_obj = cls.get_multi(*args, **kws)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for obj in multi_obj:
                executor.submit(cls.query_status, obj)


class RenRenStatusQuery(CooperationStatusQueryMixin):
    status_query_url = 'http://60.205.108.209/v1/clue/status'

    token = 'IQTPYBiB1Wk1CEHL'

    @classmethod
    def get_multi(cls, day_past=30):
        date_range = []
        now = datetime.now()
        for i in range(day_past):
            date_range.append(now - timedelta(i))
        return date_range

    @classmethod
    def _prepare_params(cls, target_datetime):
        timestamp = time.mktime(datetime.now().timetuple())
        sign = hashlib.md5(cls.token + str(timestamp)).hexdigest()
        params = {
            'sign': sign,
            'time': timestamp,
            'token': cls.token,
            'data': json.dumps({'day': target_datetime.strftime('%Y-%m-%d')})
        }
        return params

    @classmethod
    def _query(cls, params):
        req = requests.post(cls.status_query_url, data=params)
        return req

    @classmethod
    def _resolve_resp(cls, response):
        status_code = response['status']
        if status_code != 200:
            raise Exception('RenRenChe status code error')
        data_items = response['data']
        if not data_items:
            raise Exception('RenRenChe return empty')
        return data_items

    @classmethod
    def _update_status(cls, data, target_datetime):
        for k, v in data.items():
            push_records = PushCarToCooperation.objects.filter(trade_car__phone=k, create_time__day=target_datetime.day,
                                                               dealer_name=u'人人车',
                                                               create_time__month=target_datetime.month,
                                                               create_time__year=target_datetime.year)
            if push_records:
                for push_record in push_records:
                    info = v.get('deal_status')
                    if info in ('重复数据', '未开站城市', '车商车'):
                        push_record.status = 'C'
                    elif info in ('邀约失败',):
                        push_record.status = 'D'
                    else:
                        push_record.status = 'P'
                    push_record.save()
                    store_record(push_record, info)


class TianTianPaiCheStatusQuery(CooperationStatusQueryMixin):
    status_query_url = 'http://openapi.ttpai.cn/api/v2.0/query_ttp_sign_up'

    @classmethod
    def _prepare_params(cls, push_record):
        if push_record.create_time < datetime(year=2016, month=10, day=18, hour=17, minute=0, second=0):
            source = '2-198-642'
        elif push_record.trade_car.source == 'api':
            source = '2-198-645'
        elif push_record.source == 'sms_script':
            source = '2-198-644'
        elif push_record.source == 'cs_service':
            source = '2-198-643'
        else:
            source = '2-198-645'
        data = {
            'id': push_record.index_id,
            'source': source
        }
        return data

    @classmethod
    def _query(cls, params):
        response = requests.get(cls.status_query_url, params=params)
        return response

    @classmethod
    def _resolve_resp(cls, response):
        status_code = response['status']
        if status_code != 200:
            raise Exception('TianTianPaiChe status code error')
        data = response.json()
        if data['error']:
            raise Exception('TianTianPaiChe ' + data['error'])
        return data

    @classmethod
    def _update_status(cls, resp, push_record):
        auction = '竞拍' + resp['result']['auction'] if resp['result']['auction'] else '未竞拍'
        deal = '成交' + resp['result']['deal'] if resp['result']['deal'] else '未成交'
        detection = '检测' + resp['result']['detection'] if resp['result']['detection'] else '未检测'
        invite = '邀约' + resp['result']['invite'] if resp['result']['invite'] else '未邀约'
        info = ','.join((invite, detection, auction, deal))
        if '成功' in deal:
            push_record.status = 'Y'
        elif '失败' in info:
            push_record.status = 'D'
        else:
            push_record.status = 'P'
        push_record.save()
        store_record(push_record, info)

    @classmethod
    def get_multi(cls, items=None):
        return items or get_push_record('天天拍车')


if __name__ == '__main__':
    RenRenStatusQuery.bunch_query()
    TianTianPaiCheStatusQuery.bunch_query()
