#!/usr/bin/python
# -*- coding: utf-8 -*-

from proxy import Proxy_IP
from tool import fetch
from setting import fetch_url, jsonpath
import json
from decimal import Decimal
from log import logger
from db import delete_proxy_from_db
from utils.sendmail import sendMail

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
        fetch_result = fetch(url=fetch_url, proxy=proxyurl, proxy_type='https')
        response = fetch_result['response_status_code']
        if response == 200:
            one_proxy_data_dic = {"proxy": proxyurl, "proxy_scheme": proxy.type}
            data.append(one_proxy_data_dic)
            logger.info("from db add proxyinfo:{} ".format(one_proxy_data_dic))
        else:
            logger.info("proxy response is not 200, proxy info:{}, response_status_code:{}".format(proxyurl, response))
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
                fetch_result = fetch(url=fetch_url, proxy=proxyurl, proxy_type='https')
                response = fetch_result['response_status_code']
                if response == 200:
                    data.append(proxy)
                    logger.info("from jsonfile add proxyinfo:{} ".format(proxy))
                else:
                    logger.info("proxy response is not 200, proxy info:{}, response_status_code:{}".format(proxyurl, response))
    return data

def write_proxy():
    dbproxy = db_proxy()
    jsonproxy = json_proxy()
    mergeproxy = dbproxy + jsonproxy
    httpproxy = {"proxy_scheme": "http", "proxy": "http://192.168.88.176:3888"}
    mergeproxy.append(httpproxy)
    logger.info("final proxyinfos:{} ".format(mergeproxy))
    if len(mergeproxy) >=2:
        f = open(jsonpath, 'w', encoding="utf8")
        f.seek(0)
        f.truncate()
        f.write(json.dumps(list(set(mergeproxy)), ensure_ascii=False)+"\n")
        f.close()
        logger.info("Write Json Success!")
    else:
        subcontent = "没有可用的https代理"
        content = mergeproxy + "\n" + "没有可用的https代理,请管理员登录处理！"
        frominfo = "告警邮件"
        sendMail(subcontent=subcontent, content=content, frominfo=frominfo)
        logger.info("Update Error! No Available Https Proxy, SendMail To Admin!")

if __name__ == "__main__":
    write_proxy()