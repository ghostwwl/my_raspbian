#!/usr/bin/python3
#-*- coding:utf-8 -*-

# ********************************
#    FileName: main.py
#    Author  : ghostwwl
#    Email   : ghostwwl@gmail.com
#    Date    : 2019/12/21
#    Note    :
# ********************************

#   0. 硬件传感器(视频，音频，其它传感器)
#   1. 消息发送服务
#   2. 视频录像服务
#   3. 事件检测模块
#   4. 传感器数据采集

# 场景1:
#   指定的人出现在摄像头画面 --> 拍照，发通知给指定人或家庭成员
#
# 场景2:
#   陌生人出现在摄像头画面 --> 拍照，发通知
#
# 功能性场景1:
#   TFLite 检测到特定的物品
#
# 传感器场景2:
#   一氧化碳传感器 干嘛呢。。。
#   哭声
#   火灾：烟雾传感器 + 温度传感器
#   煤气泄漏：煤气传感器

import os
import time
import uuid
import datetime
import numpy as np
import threading
import cv2
from PIL import Image, ImageDraw, ImageFont

import face_recognition
from GThread import Class_Timer
from util import time_now, BaseObject, GTraceback
from NoticeDevice import NoticeDevice
from VideoRecordDevice import VideoRecordDevice
from notices import NoticeMsg
from FaceRecognitionModel import FaceRecognitionModel


CONST_FONT_STYLE = "./font/msyh.ttf"
#-----------------------------------------------------------------------------------------
class GCamService(BaseObject):
    def __init__(self, dervice_id = 0, face_encoding_path ="./known_face", video_out_path="./video", photo_out_path='./photo'):
        super(GCamService, self).__init__()

        self.debug = True
        # 人脸分类模型
        self.RecognitionModel = FaceRecognitionModel(self)
        # 视频录像设备
        self.VideoWriterDevice = VideoRecordDevice(self)
        # 事件通知设备
        self.EventNoticeDervice = NoticeDevice(self)
        # 模拟 硬件编号 服务后台将来对指定设备管理 比喻远程配置
        self.DERVICE_ID = str(uuid.uuid1())
        # 当前要启用的视频设备id 一个机器可以有N个摄像头
        self._cam_dervice_id = dervice_id
        self.video_capture = None
        self.frame_width = 0
        self.frame_height = 0
        self._face_encoding_path = face_encoding_path
        self._video_write = None

        self.NEED_RECORD_FLAG = False

        self.RECOGITION_MODEL = 'knn'

        self.PHOTO_OUT_PATH = photo_out_path
        self.VIDEO_OUT_PATH = video_out_path

        self.KNOWN_FACE_ENCODINGS = []
        self.KNOWN_FACE_NAMES = []
        self.TERMINATED = False

        self.TIMER_DERVICE = Class_Timer()

    def draw_zhcn_text(self, frame, text, pos, textColor=(255, 255, 0), textSize=30):
        """
        视频帧插入中文

        :param img:
        :param text:
        :param pos:
        :param textColor:
        :param textSize:
        :return:
        """
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        fontStyle = ImageFont.truetype(CONST_FONT_STYLE, textSize, encoding="utf-8")
        ImageDraw.Draw(img).text(pos, text, textColor, font=fontStyle)
        return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

    def add_face(self, face_encodings, face_name: str):
        """
        添加一张已知图片到摄像头

        :param face_encodings:      人脸特征编码
        :param face_name:           人脸label
        :return:
        """
        self.KNOWN_FACE_ENCODINGS.append(face_encodings)
        self.KNOWN_FACE_NAMES.append(face_name)
        pass

    def save_photo(self, frame, label):
        """
        储存图像帧 到图片
        :param frame:       图像帧
        :param label:       帧的相关 label
        :return:
        """
        if not os.path.exists(self.PHOTO_OUT_PATH):
            try:
                os.makedirs(self.PHOTO_OUT_PATH)
            except:
                self.loger.error('mkdirs `{}` err.({})'.format(self.PHOTO_OUT_PATH, GTraceback()))

        time_now_label = time_now().strftime('%Y%m%d_%H_%M_%S')
        out_path = os.path.join(self.PHOTO_OUT_PATH, '{}.jpg'.format(time_now_label))
        # JPEG 图像质量 0-100 默认 95
        save_flag = cv2.imwrite(out_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        self.loger.info('save photo `{}` --> {}'.format(out_path, save_flag))

        return save_flag, out_path
        # png 压缩级别 0-9
        # cv2.imwrite(out_path, frame, [int(cv2.IMWRITE_PNG_COMPRESSION), 5])

    def img2array(self, img_file, mode='RGB'):
        """
        加载一张图片 返回图片 np.array

        :param img_file:
        :param mode: format to convert the image to. Only 'RGB' (8-bit RGB, 3 channels) and 'L' (black and white) are supported.
        :return: image contents as numpy array
        """
        im = Image.open(img_file)
        if mode:
            im = im.convert(mode)
        return np.array(im)

    def get_face_encodings(self, face_image, known_face_locations=None, num_jitters=1):
        """
        Given an image, return the 128-dimension face encoding for each face in the image.

        :param face_image: The image that contains one or more faces
        :param known_face_locations: Optional - the bounding boxes of each face if you already know them.
        :param num_jitters: How many times to re-sample the face when calculating encoding. Higher is more accurate, but slower (i.e. 100 is 100x slower)
        :return: A list of 128-dimensional face encodings (one for each face in the image)
        """
        raw_landmarks = face_recognition.api._raw_face_landmarks(face_image, known_face_locations, model="large")
        return [np.array(face_recognition.api.face_encoder.compute_face_descriptor(face_image, raw_landmark_set, num_jitters)) for raw_landmark_set in raw_landmarks]

    def load_known_face(self):
        """
        加载已知的人像特征 确保每张图里只有一个人 这里就不去做判别了

        :return:
        """
        if not os.path.join(self._face_encoding_path):
            self.loger.error('face_encoding_path `{}` not exist'.format(self._face_encoding_path))
            return

        for cur_path, cur_dirs, cur_files in os.walk(self._face_encoding_path):
            if not len(cur_files) > 0:
                continue

            face_name = os.path.basename(cur_path)
            face_img_count = 0
            for face_file in cur_files:
                try:
                    face_img_count += 1
                    face_encoding = self.get_face_encodings(self.img2array(os.path.join(cur_path, face_file)))[0]
                    self.add_face(face_encoding, face_name)
                    self.loger.info('load `{}`: `{}` to 128-dimension feature [ OK ]'.format(face_name, face_file))
                except:
                    self.loger.error('load `{}` --> `{}` image err.({})'.format(face_name, face_img_file, GTraceback()))
            self.loger.info('load `{}` --> `{}` images'.format(face_name, face_img_count))

        # 开始训练
        getattr(self.RecognitionModel, '{0}_train'.format(self.RECOGITION_MODEL))()

    def save_to_video(self, frame):
        """
        录像

        :param frame_stream:
        :return:
        """

        out_file = os.path.join(self.VIDEO_OUT_PATH, time_now().strftime('%Y%m%d.avi'))
        if not os.path.exists(out_file) or self._video_write is None:
            self.init_video_writer(out_file)

        self._video_write.write(frame)
        pass

    def init_video_writer(self, out_video_file):
        if not os.path.exists(self.VIDEO_OUT_PATH):
            try:
                os.makedirs(self.VIDEO_OUT_PATH)
            except:
                self.loger.error('mkdirs `{}` err.({})'.format(self.VIDEO_OUT_PATH, GTraceback()))

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        # fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
        self._video_write = cv2.VideoWriter(out_video_file, fourcc, 30, (self.frame_width, self.frame_height))


    def init_cam(self):
        try:
            if self.video_capture is None:
                self.video_capture = cv2.VideoCapture(self._cam_dervice_id)

            elif self.video_capture.isOpened():
                self.video_capture = cv2.VideoCapture(self._cam_dervice_id)

            if not self.video_capture.isOpened():
                raise Exception('camera initialization failed')
        except:
            self.loger.error("{}".format(GTraceback()))
            exit()

        self.loger.info('camera initialization... width:{} height: {} fps:{}'.format(
            self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH),
            self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT),
            self.video_capture.get(cv2.CAP_PROP_FPS))
        )

        self.frame_width = 640
        self.frame_height = 480

        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        self.video_capture.set(cv2.CAP_PROP_FPS, 30)

    def the_same_stranger_filter(self):
        pass

    def event_check(self, frame, current_person, stranger_encoding=None):
        """
        事件检测
        :param frame:               待检测视频帧
        :param current_person:      视频中的识别的label
        :param stranger_encoding:   陌生人 lable 的 面部特征编码
        :return:
        """
        # 这里是事件检测， 数据来源 传感器数据、 当前摄像头帧、 当前音频采样
        # todo: 这里可以独立进程 用 zmq 通信

        event_code = 0
        # 非家庭成员出现
        if 'Unknown' in current_person:
            # 保存包含陌生人的照片
            # todo: 要加对陌生人取特征 对一定时间段同一陌生人出现 做过滤 避免重复拍照和通知
            # ret, img_file_path = self.save_photo(frame, 'Unknown')
            msg = NoticeMsg()
            msg.msg_title = '发现陌生人'
            # msg.msg_img = img_file_path
            msg.msg_body = "{}]您家发现陌生人出没，已经拍照取证".format(msg.msg_time.strftime('%Y/%m/%d %H:%M:%S'))
            # self.EventNoticeDervice.add_msg(msg)
            event_code += 1
            pass

        # 指定的人出现
        if '吴乐' in current_person:
            msg = NoticeMsg()
            msg.msg_title = '孩子放学到家了'
            msg.msg_body = "{}]您家{}孩子，安全到家了".format(msg.msg_time.strftime('%Y/%m/%d %H:%M:%S'), 'xxxx')
            # self.EventNoticeDervice.add_msg(msg)
            event_code += 2
            pass

        # todo: 这里调用远程事件检测接口

        return event_code

    def stop(self):
        """
        系统停止 释放硬件资源
        :return:
        """
        self.TERMINATED = True
        self.TIMER_DERVICE.Stop()
        if self.video_capture is not None:
            try:
                self.video_capture.release()
            except: pass

        if self._video_write is not None:
            try:
                self._video_write.release()
            except: pass

    def run_with_model(self):
        self.load_known_face()
        self.init_cam()
        self.VideoWriterDevice.start()
        self.EventNoticeDervice.start()

        while True:
            ret, frame = self.video_capture.read()

            # 保存不带绘图的帧
            src_frame = frame.copy()

            if self.NEED_RECORD_FLAG:
                # 需要录像 推送帧到录像队列
                self.VideoWriterDevice.add_frame(src_frame)

            rgb_frame = frame[:, :, ::-1]

            # 找到所有的 脸 和 脸对应的特征
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = self.get_face_encodings(rgb_frame, face_locations)

            name = "Unknown"

            current_person = set()
            for face_inx, (top, right, bottom, left) in enumerate(face_locations):
                face_encoding = face_encodings[face_inx]
                # 没有已知家庭成员人脸特征情况 摄像头刚买回的时候
                if not self.KNOWN_FACE_ENCODINGS:
                    continue

                names = getattr(self.RecognitionModel, '{0}_predict'.format(self.RECOGITION_MODEL))(face_encoding)
                if names is None:
                    continue

                # 呵呵 你懂的
                top -= 50
                right += 40
                bottom += 40
                left -= 20

                name = "Unknown"
                if len(names) > 0:
                    name = names[0]
                else:
                    self.loger.info('find more {}'.format(names))

                current_person.add(name)

                box_color = (0, 0, 255)
                ok_box_color = (120, 150, 0)
                font_color = (255, 255, 255)

                rectangle_bottom = bottom - 35
                rectange_coloe = box_color if 'Unknown' == name else ok_box_color

                cv2.rectangle(frame, (left, top), (right, bottom), rectange_coloe, 2)
                cv2.rectangle(frame, (left, rectangle_bottom), (right, bottom), rectange_coloe, cv2.FILLED)

                frame = self.draw_zhcn_text(frame, name, (left + 6, bottom - 36), font_color, 28)

            # 事件检测
            CURRENT_EVENT_CODE = self.event_check(src_frame, current_person)

            # 模拟只出现指定的人的时候录像
            self.NEED_RECORD_FLAG = True if CURRENT_EVENT_CODE in (2, 3) else False

            cv2.imshow('GCamVideo', frame)
            hit_key = cv2.waitKey(10) & 0xFF
            # 退出
            if 113 == hit_key:
                self.loger.info('user hit `q` on the keyboard to quit')
                self.stop()
                break
            # 拍照 可用于登录新家庭成员
            elif 116 == hit_key:
                self.save_photo(src_frame, name)

        try:
            self.stop()
            cv2.destroyAllWindows()
        except:
            pass


    def run(self):
        self.load_known_face()
        self.init_cam()
        self.VideoWriterDevice.start()
        self.EventNoticeDervice.start()

        while True:
            ret, frame = self.video_capture.read()

            # 保存不带绘图的帧
            src_frame = frame.copy()

            if self.NEED_RECORD_FLAG:
                # 需要录像 推送帧到录像队列
                self.VideoWriterDevice.add_frame(src_frame)

            rgb_frame = frame[:, :, ::-1]
            # rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 找到所有的 脸 和 脸对应的特征
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = self.get_face_encodings(rgb_frame, face_locations)

            name = "Unknown"

            current_person = set()
            for face_inx, (top, right, bottom, left) in enumerate(face_locations):
                face_encoding = face_encodings[face_inx]
                # 没有已知家庭成员人脸特征情况 摄像头刚买回的时候
                if not self.KNOWN_FACE_ENCODINGS:
                    continue

                matches = face_recognition.compare_faces(self.KNOWN_FACE_ENCODINGS, face_encoding, tolerance=0.45)
                # 呵呵 你懂的
                top -= 50
                right += 40
                bottom += 40
                left -= 20

                name = "Unknown"

                # 直接取匹配到的第一个 因为一个人可能有N张 特征图片编码
                # if True in matches:
                #     first_match_index = matches.index(True)
                #     name = self.KNOWN_FACE_NAMES[first_match_index]

                # 根据匹配度取最相似的
                face_distances = face_recognition.face_distance(self.KNOWN_FACE_ENCODINGS, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.KNOWN_FACE_NAMES[best_match_index]
                current_person.add(name)

                box_color = (0, 0, 255)
                ok_box_color = (120, 150, 0)
                font_color = (255, 255, 255)

                rectangle_bottom = bottom - 35
                rectange_coloe = box_color if 'Unknown' == name else ok_box_color

                cv2.rectangle(frame, (left, top), (right, bottom), rectange_coloe, 2)
                cv2.rectangle(frame, (left, rectangle_bottom), (right, bottom), rectange_coloe, cv2.FILLED)

                frame = self.draw_zhcn_text(frame, name, (left + 6, bottom - 36), font_color, 28)

            # 事件检测
            CURRENT_EVENT_CODE = self.event_check(src_frame, current_person)

            # 模拟只出现指定的人的时候录像
            self.NEED_RECORD_FLAG = True if CURRENT_EVENT_CODE in (2, 3) else False

            cv2.imshow('GCamVideo', frame)
            hit_key = cv2.waitKey(10) & 0xFF
            # 退出
            if 113 == hit_key:
                self.loger.info('user hit `q` on the keyboard to quit')
                self.stop()
                break
            # 拍照 可用于登录新家庭成员
            elif 116 == hit_key:
                self.save_photo(src_frame, name)


        try:
            self.stop()
            cv2.destroyAllWindows()
        except:
            pass

if __name__ == '__main__':
    # TT = MailSender()
    # TT.email('你们家娃到家了！！！',  mail_to='15810928108@139.com')
    T = GCamService()
    # T.run()
    T.run_with_model()

