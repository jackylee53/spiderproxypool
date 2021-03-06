#!/usr/bin/env python
# encoding: utf-8
import os
import logging
from logging.handlers import SMTPHandler, TimedRotatingFileHandler
from setting import logdir

# 判断日志文件目录是否存在
existsdir = os.path.exists(logdir)
if not existsdir:
    os.makedirs(logdir)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # 输出到控制台的log等级的开关
# 创建该handler的formatter
logger_format = logging.Formatter(
    fmt='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
console_handler.setFormatter(logger_format)
logger.addHandler(console_handler)
file_handler = TimedRotatingFileHandler(filename=os.path.join(logdir, 'log.txt'), when="midnight", backupCount=10)
file_handler.suffix = "%Y-%m-%d.txt"
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logger_format)
logger.addHandler(file_handler)

mail_handler = SMTPHandler(
    mailhost='smtp.126.com',
    fromaddr='sihuamail@126.com',
    toaddrs='sihuamail@126.com',
    subject='这是一封proypool项目发来的邮件',
    credentials=('sihuamail@126.com', ''))

mail_handler.setLevel(logging.ERROR)
mail_handler.setFormatter(logger_format)
logger.addHandler(mail_handler)
