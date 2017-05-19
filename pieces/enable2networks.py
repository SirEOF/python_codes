# coding=utf-8
"""
内外网共存脚本

使用方法
1. 连接wifi, 认证
2. 插入内网有线
3. sudo 运行此脚本(这一步可以通过alias简化, 毕竟每次断开网络的时候会重置路由, 需要重新调用脚本比较麻烦)
"""
import os
import subprocess

from pyroute2 import NetlinkError
from pyroute2.iproute import IPRoute


def get_interfaces():
    """
    获取接口列表
    :return: 环回口列表, 以太网口列表, wifi接口列表, 其他接口列表
    """
    eths = []
    los = []
    wlans = []
    others = []

    interfaces = os.listdir('/sys/class/net/')
    for i in interfaces:
        if i.startswith('e'):
            eths.append(i)
        elif i.startswith('w'):
            wlans.append(i)
        elif i.startswith('lo'):
            los.append(i)
        else:
            others.append(i)
    return los, eths, wlans, others


def delete_false_default_routes(default_interface):
    """
    删除不是指定接口的默认路由
    :param default_interface: str 默认接口 
    """
    output = subprocess.check_output('ip route | grep default', shell=True)
    default_routes = [r for r in output.split('\n') if r]
    is_default_interface_settled = False
    for route in default_routes:
        if default_interface in route:
            is_default_interface_settled = True
        else:
            subprocess.call('sudo ip route del ' + route, shell=True)
    if not is_default_interface_settled:
        raise ValueError('default route should be set previously')


def enable_static_routes(static_routes):
    """
    启用默认路由
    :param static_routes: list 默认路由列表
    """
    with IPRoute() as route:
        for r in static_routes:
            if_id = route.link_lookup(ifname=r['interface'])[0] if 'interface' in r else None
            args = {
                'dst': r['net'],
                'oif': if_id,
                'gateway': r.get('gateway'),
                'metric': 1
            }
            args = {k: v for k, v in args.iteritems() if v}
            try:
                route.route('add', **args)
            except NetlinkError as e:
                if e.code == 17:
                    continue
                else:
                    raise


if __name__ == '__main__':
    los, eths, wlans, others = get_interfaces()

    # 互联网接口
    default_interface = wlans[0]
    # 静态路由
    static_routes = [
        {
            'net': '172.16.1.0/24',
            'interface': eths[0],
        },
        {
            'net': '192.168.1.0/24',
            'gateway': '172.16.1.1',
        }
    ]
    delete_false_default_routes(default_interface)
    enable_static_routes(static_routes)
