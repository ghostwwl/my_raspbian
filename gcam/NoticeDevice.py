#!/usr/bin/python
#-*- coding: utf-8 -*-


# ********************************
#    FileName: NoticeDevice.py
#    Author  : ghostwwl
#    Email   : ghostwwl@gmail.com
#    Date    : 2019/12/21
#    Note    :
# ********************************


__author__ = "ghostwwl"

import time
import threading
import datetime
from queue import Queue
from util import time_now,  GTraceback
from notices import NoticeMsg, WxSender, MailSender


class NoticeDevice(threading.Thread):
    def __init__(self, parent):
        self.NoticeQueue = Queue()
        self.ReviceNoticeUsers = []
        self.parent = parent
        threading.Thread.__init__(self, name="NoticeSenderThread")
        self.setDaemon(1)
        self.WechatSender = WxSender()
        self.MailSender = MailSender()
        self._last_init_time = time_now()

    def add_msg(self, msg_obj):
        self.NoticeQueue.put(msg_obj)
        return self.NoticeQueue.qsize()

    def run(self):
        last_msg = ""
        while 1:
            try:
                if self.parent.TERMINATED:
                    break

                msgobj = None
                try:
                    msgobj = self.NoticeQueue.get_nowait()
                except:
                    time.sleep(0.05)
                    continue

                if msgobj is not None:
                    sbn = msgobj.msg_body.split(']', 1)[-1]
                    skip_num = 0
                    if last_msg == sbn and time_now() + datetime.timedelta(seconds=1800) > self._last_init_time:
                        skip += 1
                        if skip_num % 10 == 0:
                            self.parent.loger.debug('skip msg `{}`'.format(sbn))
                        time.sleep(0.005)
                        continue

                    self._last_init_time = time_now()
                    last_msg = sbn

                    try:
                        # 发送微信通知
                        self.parent.loger.debug('send wechat notice')
                        # self.WechatSender.do_send(msgobj, '')
                    except: pass

                    try:
                        # 发送email 通知 139邮箱(中国移动他们家的) 收到 邮件可以设置给指定手机发短信提示
                        self.parent.loger.debug('send email notice')
                        # self.MailSender.do_send(msgobj, '')
                    except: pass

                time.sleep(0.01)
            except Exception as e:
                self.parent.loger.warn('{} err.({})'.format(self.getName(), GTraceback()))


if __name__ == '__main__':
    pass