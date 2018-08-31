#!/usr/bin/env python
# encoding: utf-8
import datetime
from peewee import DoesNotExist
from log import logger
from proxy import Proxy_IP, proxypool_database


def db_init():
    proxypool_database.connect()
    proxypool_database.create_table(Proxy_IP, safe=True)


def save_proxy_to_db(proxy):
    try:
        saved_proxy = Proxy_IP.get(Proxy_IP.ip_and_port == proxy.ip_and_port)
        saved_proxy.round_trip_time = proxy.round_trip_time
        saved_proxy.anonymity = proxy.anonymity
        saved_proxy.country = proxy.country
        saved_proxy.timestamp = datetime.datetime.now()
        if saved_proxy.save() == 1:
            logger.info("{} updated into database".format(saved_proxy))
    except DoesNotExist:
        proxy.all_times = '1'
        proxy.right_times = '0'
        proxy.timestamp = datetime.datetime.now()
        if proxy.save() == 1:
            logger.info("{} saved into database".format(proxy))


def delete_proxy_from_db(proxy):
    try:
        saved_proxy = Proxy_IP.get(Proxy_IP.ip_and_port == proxy.ip_and_port)
        if saved_proxy.delete_instance() == 1:
            logger.info("{} deleted from database".format(proxy))
    except DoesNotExist:
        pass

# res代表代理的结果,成功为1,失败为0
def update_proxy_score(proxy, res=0):
    try:
        saved_proxy = Proxy_IP.get(Proxy_IP.ip_and_port == proxy.ip_and_port)
        all_times = int(saved_proxy.all_times)
        right_times = int(saved_proxy.right_times)
        saved_proxy.all_times = str(all_times + 1)
        saved_proxy.timestamp = datetime.datetime.now()
        # 计算重试过程中代理成功的次数
        if res:
            saved_proxy.right_times = str(right_times + 1)
        else:
            saved_proxy.right_times = str(right_times - 1)
        # 根据成功次数判断对代理的操作
        if int(saved_proxy.right_times) <= 0:
            # 执行删除记录操作
            if saved_proxy.delete_instance() == 1:
                logger.info("instability proxy:{} deleted from database".format(proxy))
            else:
                logger.info("delete fail, nstability proxy:{}".format(proxy))
        else:
            if saved_proxy.save() == 1:
                logger.info("{} update from database, new all_times:{}, new right_times:{}"\
                        .format(proxy, saved_proxy.all_times, saved_proxy.right_times))
    except DoesNotExist:
        proxy.all_times = '1'
        proxy.right_times = '0'
        proxy.timestamp = datetime.datetime.now()
        if proxy.save() == 1:
            logger.info("{} saved into database".format(proxy))

if __name__ == "__main__":
    pass
