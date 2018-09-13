#!/usr/bin/python
# -*- coding: utf-8 -*-

from proxy import Proxy_IP
from tool import fetch
from setting import fetch_url, jsonpath
import json
import re
import datetime
from decimal import Decimal
from log import logger
from db import update_proxy_score, save_proxy_to_db
from utils.sendmail import sendMail
from functools import reduce

default_proxy = [{"proxy_scheme": "http", "proxy": "http://192.168.88.176:3888"},\
                 {"proxy_scheme": "https", "proxy": "http://192.168.88.155:3888"},\
                 {"proxy_scheme": "http", "proxy": "http://192.168.88.155:3888"}]

def default(obj):
    if isinstance(obj, Decimal):
        return int(obj)
    raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)

def db_proxy():
    data = []
    proxies = Proxy_IP.select().where(Proxy_IP.type == 'https').order_by(Proxy_IP.timestamp)
    for proxy in proxies:
        r_times = int(proxy.right_times)
        a_times = int(proxy.all_times)
        success_rate = r_times*1.0/a_times
        ip_and_port = proxy.ip_and_port
        httptype = proxy.type
        proxyurl = httptype + "://" + ip_and_port
        fetch_result = fetch(url=fetch_url, proxy=proxyurl, proxy_type='https')
        response = fetch_result['response_status_code']
        # 成功率超过30%的代理在DB中增加成功次数
        if success_rate > 0.3 and response == 200:
            update_proxy_score(proxy, res=1)
            one_proxy_data_dic = {"proxy": proxyurl, "proxy_scheme": proxy.type}
            data.append(one_proxy_data_dic)
            logger.info("from db add proxyinfo:{} ".format(one_proxy_data_dic))
        # 成功率低于30%的代理在DB中减少成功次数,成功次数低于0则删除记录
        else:
            logger.info("proxy response is not 200, proxy info:{}, response_status_code:{}".format(proxyurl, response))
            # delete_proxy_from_db(proxy)
            update_proxy_score(proxy)
    return data

def json_proxy():
    data = []
    jsonfile = open(jsonpath, encoding='utf-8')
    proxylist = json.load(jsonfile)
    if proxylist:
        for proxy in proxylist:
            proxyurl = proxy['proxy']
            # 端口是3888的为私有代理
            pattern = ':3888$'
            if not re.search(pattern, proxyurl):
            # if proxyurl != "http://192.168.88.176:3888":
                fetch_result = fetch(url=fetch_url, proxy=proxyurl, proxy_type='https')
                response = fetch_result['response_status_code']
                # 查询代理IP是否在DB中
                ip_and_port = proxyurl.split('/')[-1]
                httptype = proxyurl.split(':')[0]
                proxies = Proxy_IP.select().where(Proxy_IP.ip_and_port == ip_and_port, Proxy_IP.type == httptype).first()
                # print("proxies", proxies)
                # 构建对象
                proxyinfo = Proxy_IP(ip_and_port=ip_and_port)
                proxyinfo.ip_and_port = ip_and_port
                proxyinfo.timestamp = datetime.datetime.now()

                if proxies:
                    # IP在DB中
                    if response == 200:
                        update_proxy_score(proxyinfo, res=1)
                        data.append(proxy)
                        logger.info("from jsonfile add proxyinfo:{} ".format(proxy))
                    else:
                        update_proxy_score(proxyinfo)
                        logger.info("proxy response is not 200, cancel from jsonfile, proxy info:{} ".format(proxy))
                else:
                    # IP不在DB中
                    proxyinfo.type = 'https'
                    proxyinfo.anonymity = 'high_anonymity'
                    proxyinfo.round_trip_time = '1'
                    proxyinfo.country = 'China'
                    proxyinfo.all_times = '1'
                    proxyinfo.timestamp = datetime.datetime.now()
                    if response == 200:
                        proxyinfo.right_times = '1'
                        save_proxy_to_db(proxyinfo)
                        data.append(proxy)
                        logger.info("from jsonfile add proxyinfo:{} ".format(proxy))
                    else:
                        proxyinfo.right_times = '1'
                        save_proxy_to_db(proxyinfo)
                        logger.info("proxy response is not 200, cancel from jsonfile, proxy info:{} ".format(proxy))
    return data

def write_proxy():
    # 获取从DB中查询https代理的记录
    dbproxy = db_proxy()
    # 获取从已有Json中查询https代理的记录
    jsonproxy = json_proxy()
    # 合并代理记录,并添加默认代理
    mergeproxy = dbproxy + jsonproxy + default_proxy
    # 代理去重
    f = lambda x, y: x if y in x else x + [y]
    mergeproxy = reduce(f, [[], ] + mergeproxy)
    logger.info("final proxyinfos:{} ".format(mergeproxy))
    # 预警
    if len(mergeproxy) >= 2:
        f = open(jsonpath, 'w', encoding="utf8")
        f.seek(0)
        f.truncate()
        f.write(json.dumps(mergeproxy, ensure_ascii=False)+"\n")
        f.close()
        logger.info("Write Json Success!")
    else:
        subcontent = "没有可用的https代理"
        content = str(mergeproxy) + "\n" + "没有可用的https代理,请管理员登录处理！"
        frominfo = "告警邮件"
        sendMail(subcontent=subcontent, content=content, frominfo=frominfo)
        logger.info("Update Error! No Available Https Proxy, SendMail To Admin!")

if __name__ == "__main__":
    write_proxy()