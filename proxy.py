#!/usr/bin/env python
# encoding: utf-8
import datetime
from peewee import *

from setting import CURRENT_DIR

proxypool_database = SqliteDatabase(CURRENT_DIR + '/proxypool.db')


class Proxy_IP(Model):
    ip_and_port = CharField()
    type = CharField(default="http")
    round_trip_time = DoubleField(null=True)
    country = CharField(null=True)
    anonymity = CharField(null=True)
    all_times = CharField(null=True)
    right_times = CharField(null=True)
    timestamp = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return self.type + "://" + self.ip_and_port

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if isinstance(other, Proxy_IP):
            return str(self) == str(other)

    class Meta:
        database = proxypool_database


if __name__ == "__main__":
    print(CURRENT_DIR + '/proxypool.db')
