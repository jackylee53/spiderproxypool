#!/usr/bin/env python
# encoding: utf-8
import random

import requests
import time

from proxy import Proxy_IP
from setting import USER_AGENT_LIST, TIME_OUT, RETRY_NUM


def fetch(url, proxy=None, proxy_type='http'):
    kwargs = {
        "headers": {
            "User-Agent": random.choice(USER_AGENT_LIST),
            'accept-language': 'zh-CN,zh;q=0.8',
        },
        "timeout": TIME_OUT,
    }
    response = None
    response_status_code = None
    retry_num = start = end = 0
    for i in range(RETRY_NUM):
        try:
            if proxy is not None:
                kwargs["proxies"] = {
                    proxy_type: str(proxy)}
            start = time.time()
            response = requests.get(url, **kwargs)
            end = time.time()
            if response:
                response_status_code = response.status_code
            break
        except Exception as e:
            time.sleep(1)
            retry_num += 1
            continue
    return {"response": response, "retry_num": retry_num, "round_trip_time": round((end - start), 2), "response_status_code": response_status_code}

if __name__ == "__main__":
    check_anonymity_url = "http://www.xxorg.com/tools/checkproxy/"
    fetch_result = fetch(check_anonymity_url, Proxy_IP(ip_and_port="194.246.105.52:53281"))
    print("fetch_result", fetch_result)
