#!/usr/bin/python
#-*- coding: utf-8 -*-

# ********************************
#    FileName: VideoRecordDevice.py
#    Author  : ghostwwl
#    Email   : ghostwwl@gmail.com
#    Date    : 2019/12/21
#    Note    :
# ********************************

__author__ = "ghostwwl"

import time
import threading
from queue import Queue


class VideoRecordDevice(threading.Thread):
    def __init__(self, parent):
        self.frame_queue = Queue()
        self.parent = parent
        threading.Thread.__init__(self, name="VideoWriterThread")
        self.setDaemon(1)

    def add_frame(self, frame):
        self.frame_queue.put(frame)

    def run(self):
        while 1:
            try:
                if self.parent.TERMINATED:
                    break

                frame = None
                try:
                    frame = self.frame_queue.get_nowait()
                except:
                    time.sleep(0.001)
                    continue

                if frame is not None:
                    self.parent.save_to_video(frame)
                else:
                    time.sleep(0.001)
            except Exception as e:
                self.parent.loger.warn('{} err.({})'.format(self.getName(), GTraceback()))


if __name__ == '__main__':
    pass