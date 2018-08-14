#!/usr/bin/python
# -*- coding: utf-8 -*-

from proxy import Proxy_IP
from tool import fetch
from setting import fetch_url, jsonpath
import json
from decimal import Decimal
from log import logger
from db import delete_proxy_from_db

def default(obj):
    if isinstance(obj, Decimal):
        return int(obj)
    raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)

def db_proxy():
    data = []
    proxies = Proxy_IP.select().where(Proxy_IP.type == 'https').order_by(Proxy_IP.timestamp)
    for proxy in proxies:
        ip_and_port = proxy.ip_and_port
        type = proxy.type
        proxyurl = type + "://" + ip_and_port
        fetch_result = fetch(fetch_url, proxyurl)
        response = fetch_result['response_status_code']
        if response == 200:
            one_proxy_data_dic = {"proxy": proxyurl, "proxy_scheme": proxy.type}
            data.append(one_proxy_data_dic)
            logger.info("from db add proxyinfo:{} ".format(one_proxy_data_dic))
        else:
            delete_proxy_from_db(proxy)
    return data

def json_proxy():
    data = []
    jsonfile = open(jsonpath, encoding='utf-8')
    proxylist = json.load(jsonfile)
    if proxylist:
        for proxy in proxylist:
            proxyurl = proxy['proxy']
            if proxyurl != "http://192.168.88.176:3888":
                fetch_result = fetch(fetch_url, proxyurl)
                response = fetch_result['response_status_code']
                if response == 200:
                    data.append(proxy)
                    logger.info("from jsonfile add proxyinfo:{} ".format(proxy))
    return data

def write_proxy():
    dbproxy = db_proxy()
    jsonproxy = json_proxy()
    mergeproxy = dbproxy + jsonproxy
    httpproxy = {"proxy_scheme": "http", "proxy": "http://192.168.88.176:3888"}
    mergeproxy.append(httpproxy)
    logger.info("final proxyinfos:{} ".format(mergeproxy))
    f = open(jsonpath, 'w', encoding="utf8")
    f.seek(0)
    f.truncate()
    f.write(json.dumps(mergeproxy, ensure_ascii=False)+"\n")
    f.close()
    logger.info("Write Json Success!")

if __name__ == "__main__":
    write_proxy()