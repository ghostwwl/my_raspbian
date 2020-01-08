#!/usr/bin/python
#-*- coding:utf-8 -*-


import cv2
import numpy as np


from PIL import Image, ImageDraw, ImageFont

def put_zhcn_text(img, text, pos, textColor=(255, 255, 0), textSize=30):
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    fontStyle = ImageFont.truetype("./msyh.ttf", textSize, encoding="ghostwwl")
    ImageDraw.Draw(img).text(pos, text, textColor, font=fontStyle)
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


video_capture = cv2.VideoCapture(0)

if not video_capture.isOpened():
    raise Exception('open cam failed')

print('width:{} height: {} fps:{}'.format(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH),
                                          video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT),
                                          video_capture.get(cv2.CAP_PROP_FPS)))

video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
video_capture.set(cv2.CAP_PROP_FPS, 60)
# video_capture.set(cv2.CAP_PROP_FOURCC, cv2.CAP_PROP_FOURCC('M', 'J', 'P', 'G'))



while True:
    ret, frame = video_capture.read()
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
