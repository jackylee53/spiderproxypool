#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import codecs
import smtplib
import datetime
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from twisted.internet import reactor
from log import logger

from_addr = 'sihuamail@126.com'
smtp_server = 'smtp.126.com'
password = 'sihuamail123'
to_addr = 'lp08082008@163.com'

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), \
                       addr.encode('utf-8') if isinstance(addr, bytes) else addr))

def sendMail(subcontent, content, frominfo):
    TDate = datetime.datetime.now().strftime('%Y-%m-%d')
    TTime = datetime.datetime.now().strftime('%H:%M')

    subject = u'%s %s %s' % (TDate, TTime, subcontent)
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = _format_addr(u'%s <%s>' % (frominfo, from_addr))
    msg['To'] = _format_addr(u'管理员 <%s>' % to_addr)
    msg['Subject'] = Header(subject, 'utf-8').encode()

    server = smtplib.SMTP(smtp_server, 25)
    server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()

if __name__ == "__main__":
    logger.info("{} Start sendMail!!! ".format(sendMail.__class__.__name__))
    subcontent = "没有可用的https代理"
    content = "没有可用的https代理,请管理员登录处理！"
    frominfo = "告警邮件"
    sendMail(subcontent=subcontent, content=content, frominfo=frominfo)
    # Execution will block here until Ctrl+C (Ctrl+Break on Windows) is pressed.
    try:
        reactor.run()
    except (KeyboardInterrupt, SystemExit):
        pass