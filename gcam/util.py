#!/usr/bin/python
#-*- coding: utf-8 -*-

# ********************************
#    FileName: util.py
#    Author  : ghostwwl
#    Email   : ghostwwl@gmail.com
#    Date    : 2019/12/21
#    Note    :
# ********************************

__author__ = "ghostwwl"

import traceback
import datetime
import logging
import functools
from timeit import default_timer

#-----------------------------------------------------------------------------------------
logging.basicConfig(format='%(levelname)-8s %(asctime)s] %(message)s', level=logging.INFO)

#-----------------------------------------------------------------------------------------
def warp_func_use_time(func):
    @functools.wraps(func)
    def clac_time_run(*args, **kwargs):
        stime = default_timer()
        try:
            func(*args, **kwargs)
        except:
            BaseObject.loger.error('do function: {0} err: {1}'.format(func.__name__, GTraceback()))
        BaseObject.loger.info('do function: {0} use: {1} seconds'.format(func.__name__, default_timer() - stime))
    return clac_time_run

#-----------------------------------------------------------------------------------------
def GTraceback():
    try:
        return traceback.format_exc()
    except:
        pass

def time_now(cur_timezone = 8):
    '''返回 东8区 当前时间'''
    return datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=cur_timezone)))


#-----------------------------------------------------------------------------------------
class BaseObject(object):
    loger = logging.getLogger()
    def __init__(self, log_file=None):
        self.debug = True
        self.loger.setLevel(logging.DEBUG if self.debug else logging.ERROR)
        self.obj_load_timepos = default_timer()
        self.log_file = log_file or None
        self.has_logfile_handler = False

    def out_log_file(self, log_file=None, log_level=1):
        '''
        添加一个文件日志输出
        :param log_file:        日志文件
        :param log_level:       日志基本 1 info 2 debug 3 warning 4 error
        :return:
        '''
        self.log_file = log_file
        f_handler = logging.FileHandler(self.log_file)
        f_handler.setFormatter(logging.Formatter("%(levelname)-8s %(asctime)s] %(message)s"))
        # f_handler.setLevel(logging.ERROR)
        f_handler.setLevel(logging.DEBUG if self.debug else logging.ERROR)
        self.loger.addHandler(f_handler)
        self.has_logfile_handler = True




if __name__ == '__main__':
    pass