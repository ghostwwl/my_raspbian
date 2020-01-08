#!/usr/bin/python
#-*- coding: utf-8 -*-

# ********************************
#    FileName: notices.py
#    Author  : ghostwwl
#    Email   : ghostwwl@gmail.com
#    Date    : 2019/12/21
#    Note    : 通知下发模块
# ********************************

__author__ = "ghostwwl"

import os
import sys
import datetime
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
import email.encoders as encoders

from util import time_now

smtp_host = 'smtp.sina.com'
smtp_port = 25
smtp_timeout = 30.0
smtp_login = 'ghostwwl@sina.com'
smtp_password = 'sinaxxxxx.xxxxxxx'

#-----------------------------------------------------------------------------------------
class NoticeMsg(object):
    __slots__ = ('_title', '_msg', '_time', '_img')
    def __init__(self, title = None, message = None, img_obj=None, msg_time =None):
        '''
        :param title:       通知标题
        :param message:     通知正文
        :param img_obj:     取证图像对象
        :param msg_time:    通知时间
        '''
        self._title = title
        self._msg = message
        self._img = img_obj
        self._time = msg_time or time_now()

    @property
    def msg_title(self):
        return self._title

    @msg_title.setter
    def msg_title(self, title):
        self._title = title

    @property
    def msg_body(self):
        return self._msg

    @msg_body.setter
    def msg_body(self, body):
        self._msg = body

    @property
    def msg_img(self):
        return self._img

    @msg_img.setter
    def msg_img(self, imgobj):
        self._img = imgobj

    @property
    def msg_time(self):
        return self._time

    @msg_time.setter
    def msg_time(self, msg_time):
        self._time = msg_time

    def __repr__(self):
        return '<class {0}> msg_time:{1} msg_title:{2} msg_body:{3}'.format(
            self.__class__.__name__, self._time, self._title, self._msg,
        )

#-----------------------------------------------------------------------------------------
class NoticeSender(object):
    def do_send(self, msg_obj, notice_user):
        raise NotImplemented()

#-----------------------------------------------------------------------------------------
class WxSender(NoticeSender):
    def do_send(self, msg_obj, notice_user):
        content = 'text={0}&desp={1}'.format(msg_obj.msg_title, msg_obj.msg_body)
        # todo：这里自己去弄server酱的通知
        url = "https://sc.ftqq.com/SCU38351T8f9d11ed939b6d9a376e0781465c259e468313b.send?%s" % content
        r = requests.get(url)
        return r.status_code

#-----------------------------------------------------------------------------------------
class MailSender(NoticeSender):
    # def do_send (self, msg_txt, subject='[INFO] 这是一封测试邮件！！！', files=[], mail_to='ghostwwl@qq.com'):

    def do_send(self, msg_obj, notice_user, files=[]):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = msg_obj.msg_title
        # 这里是测试的呢
        msg['From'] = 'ghostwwl@sina.com'
        msg['To'] = "ghostwwl@139.com"

        html = msg_obj.msg_body
        part2 = MIMEText(html, _charset='utf8')
        msg.attach(part2)
        for f in files:
            part = MIMEBase('application', 'octet-stream')
            with open(f, 'rb') as file_obj:
                part.set_payload(file_obj.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(f)))
            msg.attach(part)

        kwargs = dict(host=smtp_host, port=smtp_port)
        if smtp_timeout:
            kwargs['timeout'] = smtp_timeout

        smtp = smtplib.SMTP(**kwargs)
        if smtp_login and smtp_password:
            r = smtp.login(smtp_login, smtp_password)
            print(r)

        mailto_list = msg['To'].strip().split(",")
        if len(mailto_list) > 1:
            for mailtoi in mailto_list:
                smtp.sendmail(msg['From'], mailtoi.strip(), msg.as_string())
        else:
            smtp.sendmail(msg['From'], msg['To'], msg.as_string())

        smtp.quit()
        return True


#-----------------------------------------------------------------------------------------

if __name__ == '__main__':
    msg = NoticeMsg()
    msg.msg_title = '{}: 你们家娃到家了。。。'.format(msg.msg_time)
    msg.msg_body = "我爱北京天安门，天安门上太阳升。。。"

    T = MailSender()
    T = WxSender()
    T.do_send(msg, '')
