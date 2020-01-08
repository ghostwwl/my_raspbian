#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ****************************************************
#  FileName: GThread.py
#  Author: ghostwwl
#  Note:
#    2008.10 add states and add Class_Timer
# ****************************************************

import time
import threading
import traceback
import logging
from timeit import default_timer

__author__ = "ghostwwl (ghostwwl@gmail.com)"
__version__ = "1.0"


LOGGER = logging.getLogger("GThreadLog")
# -------------------------------------------------------------------------------
class Thread_Control(object):
    '''The Control Class'''

    def __init__(self):
        self.ControlEvent = threading.Event()
        self.ControlEvent.set()
        self.TimeOut = None
        self.Terminated = False
        self.CStateInfo = {-1: 'STOP', 0: 'READY', 1: 'RUNNING', 2: 'PAUSE'}
        self.CSTATES = 0

    def stop(self):
        self.CSTATES = -1
        LOGGER.warning('Stopping Thread %-30s [ OK ]' % (self.getName(), ))
        self.Terminated = True

    def pause(self, TimeOut=None):
        self.TimeOut = TimeOut
        self.ControlEvent.clear()
        self.CSTATES = 2

    def restore(self):
        self.ControlEvent.set()


# -------------------------------------------------------------------------------
class mythread(threading.Thread, Thread_Control):
    '''
    BaseThread Class With Control Method[stop, pause, restore]
    time dilution of precision about 1 millisecond
    thread state {-1:'STOP', 0:'READY', 1:'RUNNING', 2:'PAUSE'}
    '''

    def __init__(self, owner, ThreadName, TimeSpacing=0, TimeDelay=0):
        '''
        __init__(self, owner, ThreadName, TimeSpacing=0)
        owner         The Thread Owner
        ThreadName    The Thread Name
        TimeSpacing   Run TimeSpacing
        TimeDelay     The Thread Start TimeDelay
        '''
        self.owner = owner
        self.TimeSpacing = TimeSpacing  # 任务多长时间执行一次
        self.TimeDelay = TimeDelay
        Thread_Control.__init__(self)
        threading.Thread.__init__(self, name=ThreadName)
        self.setDaemon(1)

    def run(self):
        '''
        This While loop stop until Terminated
        This Object Has sotp, pause(timeout = None) and restore method
        '''
        if self.TimeDelay != 0:
            TSTART = self.TimeDelay
        else:
            TSTART = 0
        while 1:
            try:
                # 这里是线程的停止处理
                if self.Terminated:
                    break

                # 这里是线程的暂停处理
                if self.TimeOut is not None:
                    # 带有暂停超时的处理
                    self.ControlEvent.wait(self.TimeOut)
                    self.TimeOut = None
                    self.ControlEvent.set()
                else:
                    # 不带超时 那么必须等到线程恢复
                    self.ControlEvent.wait()

                CUR_TIMING = default_timer()
                if CUR_TIMING - TSTART > self.TimeSpacing:
                    TSTART = CUR_TIMING
                    # 这个才是我们的工作函数
                    self.CSTATES = 1
                    self.handle()

                time.sleep(0.0001)  # 暂停0.1毫秒 防止空跑占用过高cpu
            except Exception as e:
                LOGGER.error("%s Error: %s" % (self.getName(), str(traceback.format_exc())))

    # def __getattr__(self, key):
    #    #后来想了下 重载这个虽然方便 但是 打破了层次结构 还是严格层次比较好
    #    '''优先在自己的空间找 找不到到owner的空间去找'''
    #    try:
    #        if self.__dict__.has_key(key):
    #            return self.__dict__[key]
    #        if self.__dict__['owner'].__dict__.has_key(key):
    #            return self.__dict__['owner'].__dict__[key]
    #    except AttributeError, e:
    #        raise Exception("AttributeError [object has no attribute '%s']" % str(key))

    def handle(self):
        '''The Real Work Function'''
        pass

    def getstate(self):
        '''check the thread state'''
        return self.CSTATES

    def getstatemsg(self):
        return self.CStateInfo[self.CSTATES]


# -------------------------------------------------------------------------------
class Timer(mythread):
    '''
    Do Somthing in a thread
    time dilution of precision about 1 millisecond
    Timer state {-1:'STOP', 0:'READY', 1:'RUNNING', 2:'PAUSE'}
    Timer has [stop, pause, restore] Control Methods
    '''

    def __init__(self, owner, callfunc, TimerName, TimeSpacing=0, TimeDelay=0):
        '''
        __init__(self, owner, callfunc, TimerName, TimeSpacing=0, TimeDelay=0)
        '''
        self.CallFunc = callfunc
        mythread.__init__(self, owner, TimerName, TimeSpacing, TimeDelay)

    def handle(self):
        func = getattr(self.owner, self.CallFunc)
        func()


# -------------------------------------------------------------------------------
class Class_Timer(object):
    def __init__(self):
        self.Timers = {}

    # 添加一个定时处理(定时处理名称，处理函数的拥有者，定时时间，定时处理函数)
    def AddTimer(self, name, owner, timeout, ontimer, TimeDelay=0):
        '''AddTimer(self, name, owner, timeout, ontimer, TimeDelay=0)'''
        # if self.Timers.has_key(name):
        if name in self.Timers:
            return
        T = Timer(owner, ontimer, 'Timer_%s' % name, timeout)
        T.start()
        self.Timers[name] = T

    # 删除一个定时处理
    def DeleteTimer(self, name):
        '''StopTimer(self, name)'''
        try:
            T = self.Timers.pop(name, None)
            if T:
                T.stop()
        except KeyError as e:
            raise KeyError("No Timer named '%s'" % name)

    # 停止所有定时处理
    def Stop(self):
        '''Stop(self)'''
        for name in list(self.Timers.keys()):
            self.DeleteTimer(name)

    # 暂停一个定时器
    def PauseTimer(self, name, TimeOut=None):
        '''PauseTimer(self, name, TimeOut=None)'''
        try:
            self.Timers[name].pause(TimeOut)
        except KeyError as e:
            raise KeyError("No Timer named '%s'" % name)

    # 暂停所有定时器
    def Pause(self, TimeOut=None):
        '''Pause(self, TimeOut=None)'''
        for T in self.Timers.values():
            if T.getstate() != 2:
                T.pause(TimeOut)

    # 从暂停状态恢复一个定时器
    def RestoreTimer(self, name):
        '''RestoreTimer(self, name)'''
        try:
            self.Timers[name].restore()
        except KeyError as e:
            raise KeyError("No Timer named '%s'" % name)

    # 从暂停状态恢复所有定时器
    def Restore(self):
        '''Restore(self)'''
        for T in self.Timers.values():
            T.restore()


if __name__ == '__main__':
    class tt(object):
        def __init__(self, mode_file):
            super(tt, self).__init__()

            self.Timer = Class_Timer()
            # self.Setting = __import__('Setting')

        def load_config(self):
            print('--------')
            # self.Setting = __import__('Setting')
            # globals()['Setting'] = self.Setting
            # print 'xxx'

        def main(self):
            self.Timer.AddTimer('LoadConfigThread', self, 1, 'load_config')

            import time
            c = 0
            while 1:
                time.sleep(1)
                c += 1
                print('main thread ok {0}'.format(c))
                # print self.Setting.testcc
                if c > 300:
                    self.Timer.Stop()
                    break

    T = tt("")
    print( T.main() )
