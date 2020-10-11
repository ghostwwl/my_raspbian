#!/usr/bin/python3
#-*- coding:utf-8 -*-

import argparse
import numpy as np
import time

from PIL import Image

#from tflite_runtime.interpreter import Interpreter
from tensorflow.lite.python import interpreter as interpreter_wrapper
from prettytable import PrettyTable


#-----------------------------------------------------------------------------------
def load_labels(filename):
    my_labels = []
    input_file = open(filename, 'r')
    for l in input_file:
        my_labels.append(l.strip())
    return my_labels


#-----------------------------------------------------------------------------------
def run_file():
    floating_model = False
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image", default="./grace_hopper.bmp", help="image to be classified")
    parser.add_argument("-m", "--model_file", default="./mobilenet_v1_1.0_224_quant.tflite",
                        help=".tflite model to be executed")
    parser.add_argument("-l", "--label_file", default="./labels.txt", help="name of file containing labels")
    parser.add_argument("--input_mean", default=127.5, help="input_mean")
    parser.add_argument("--input_std", default=127.5, help="input standard deviation")
    parser.add_argument("--num_threads", default=4, help="number of threads")

    args = parser.parse_args()

    interpreter = interpreter_wrapper.Interpreter(model_path=args.model_file)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # check the type of the input tensor
    if input_details[0]['dtype'] == np.float32:
        floating_model = True

    # NxHxWxC, H:1, W:2
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]
    img = Image.open(args.image)
    img = img.resize((width, height))

    # add N dim
    input_data = np.expand_dims(img, axis=0)
    if floating_model:
        input_data = (np.float32(input_data) - args.input_mean) / args.input_std

    interpreter.set_num_threads(int(args.num_threads))  # <- Specifies the num of threads assigned to inference
    interpreter.set_tensor(input_details[0]['index'], input_data)

    start_time = time.time()
    interpreter.invoke()
    stop_time = time.time()

    output_data = interpreter.get_tensor(output_details[0]['index'])
    results = np.squeeze(output_data)
    top_k = results.argsort()[-5:][::-1]
    labels = load_labels(args.label_file)

    table = PrettyTable()
    table.field_names = ["置信度", "标签id", '标签名']

    for i in top_k:
        if floating_model:
            labelid, labelname = labels[i].split(':')
            table.add_row((float(results[i]), labelid, labelname))
            # print('{0:08.6f}'.format(float(results[i])) + ":", labels[i])
        else:
            labelid, labelname = labels[i].split(':')
            table.add_row((float(results[i] / 255.0), labelid, labelname))
            # print('{0:08.6f}'.format(float(results[i] / 255.0)) + ":", labels[i])

    table.align = 'l'
    print(table)
    print("用时: ", stop_time - start_time)

#-----------------------------------------------------------------------------------
def run_webcam():
    import cv2

    floating_model = False
    model_file = './mobilenet_v1_1.0_224_quant.tflite'
    label_file = './labels.txt'
    thread_num = 4
    input_mean = 127.5
    input_std = 127.5

    interpreter = interpreter_wrapper.Interpreter(model_path=model_file)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    #interpreter.set_num_threads(thread_num)

    # check the type of the input tensor
    if input_details[0]['dtype'] == np.float32:
        floating_model = True

    # NxHxWxC, H:1, W:2
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]

    # VideoCapture capture(0);
    # /*设置摄像头参数 不要随意修改
    # capture.set(CV_CAP_PROP_FRAME_WIDTH, 1080);//宽度
    # capture.set(CV_CAP_PROP_FRAME_HEIGHT, 960);//高度
    # capture.set(CV_CAP_PROP_FPS, 30);//帧数
    # capture.set(CV_CAP_PROP_BRIGHTNESS, 1);//亮度 1
    # capture.set(CV_CAP_PROP_CONTRAST,40);//对比度 40
    # capture.set(CV_CAP_PROP_SATURATION, 50);//饱和度 50
    # capture.set(CV_CAP_PROP_HUE, 50);//色调 50
    # capture.set(CV_CAP_PROP_EXPOSURE, 50);//曝光 50
    # */
    #
    # CV_CAP_PROP_POS_MSEC - 影片目前位置，为毫秒数或者视频获取时间戳
    # CV_CAP_PROP_POS_FRAMES - 将被下一步解压/获取的帧索引，以0为起点
    # CV_CAP_PROP_POS_AVI_RATIO - 视频文件的相对位置（0 - 影片的开始，1 - 影片的结尾)
    # CV_CAP_PROP_FRAME_WIDTH - 视频流中的帧宽度
    # CV_CAP_PROP_FRAME_HEIGHT - 视频流中的帧高度
    # CV_CAP_PROP_FPS - 帧率
    # CV_CAP_PROP_FOURCC - 表示codec的四个字符
    # CV_CAP_PROP_FRAME_COUNT - 视频文件中帧的总数
    # 函数cvGetCaptureProperty获得摄像头或者视频文件的指定属性。

    from PIL import Image, ImageDraw, ImageFont

    def put_zhcn_text(img, text, pos, textColor=(255, 255, 0), textSize=100):
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        fontStyle = ImageFont.truetype("/project/python/glearn/lib/data/msyh.ttf", textSize, encoding="utf-8")
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
    video_capture.set(cv2.CAP_PROP_FPS, 30)

    # print(width, height)
    labels = load_labels(label_file)

    last_label = ''
    while 1:
        ret, frame = video_capture.read()

        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        img = img.resize((width, height))

        input_data = np.expand_dims(img, axis=0)
        if floating_model:
            input_data = (np.float32(input_data) - input_mean) / input_std

        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()

        output_data = interpreter.get_tensor(output_details[0]['index'])
        results = np.squeeze(output_data)
        top_k = results.argsort()[-3:][::-1]


        labelname = ""
        only_labelname = ''
        for i in top_k:
            labelid, labelname = labels[i].split(':')
            if floating_model:
                only_labelname = labelname = labelname.split(',')[0]
                labelname = "{:.3f} | {}".format(float(results[i]), labelname)
            else:
                only_labelname = labelname = labelname.split(',')[0]
                labelname = "{:.3f} | {}".format(float(results[i] / 255.0), labelname)
            break

        if last_label != only_labelname:
            frame = put_zhcn_text(frame, labelname, (5, 5), (0, 255, 0), 30)
            # put_chi_text(img, text, pos, textColor=(255, 255, 0), textSize=100):

            # font = cv2.FONT_HERSHEY_DUPLEX
            # cv2.putText(frame, labelname, (10, 25), font, 1.0, (255, 0, 255), 1)

        cv2.imshow('Video', frame)
        # last_label = only_labelname

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()




#-----------------------------------------------------------------------------------
def run_dir(dir_name = '/home/pi/图片/test/'):
    floating_model = False
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image", default="./grace_hopper.bmp", help="image to be classified")
    parser.add_argument("-m", "--model_file", default="./mobilenet_v1_1.0_224_quant.tflite",
                        help=".tflite model to be executed")
    parser.add_argument("-l", "--label_file", default="./labels.txt", help="name of file containing labels")
    parser.add_argument("--input_mean", default=127.5, help="input_mean")
    parser.add_argument("--input_std", default=127.5, help="input standard deviation")
    parser.add_argument("--num_threads", default=4, help="number of threads")

    args = parser.parse_args()

    interpreter = interpreter_wrapper.Interpreter(model_path=args.model_file)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    interpreter.set_num_threads(int(args.num_threads))  # <- Specifies the num of threads assigned to inference

    # check the type of the input tensor
    if input_details[0]['dtype'] == np.float32:
        floating_model = True

    # NxHxWxC, H:1, W:2
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]

    import glob, os
    image_files = glob.glob(os.path.join(dir_name, '*'))
    labels = load_labels(args.label_file)

    for imagef in image_files:
        print('\n\n识别图片: `{}`'.format(imagef))
        img = Image.open(imagef)
        img = img.resize((width, height))

        # add N dim
        input_data = np.expand_dims(img, axis=0)
        if floating_model:
            input_data = (np.float32(input_data) - args.input_mean) / args.input_std

        interpreter.set_tensor(input_details[0]['index'], input_data)

        start_time = time.time()
        interpreter.invoke()
        stop_time = time.time()

        output_data = interpreter.get_tensor(output_details[0]['index'])
        results = np.squeeze(output_data)
        top_k = results.argsort()[-3:][::-1]

        table = PrettyTable()
        table.field_names = ["置信度", "标签id", '标签名']

        for i in top_k:
            if floating_model:
                labelid, labelname = labels[i].split(':')
                table.add_row((float(results[i]), labelid, labelname))
            else:
                labelid, labelname = labels[i].split(':')
                table.add_row((float(results[i] / 255.0), labelid, labelname))

        table.align = 'l'
        print(table)
        print("用时: ", stop_time - start_time)


#-----------------------------------------------------------------------------------
if __name__ == "__main__":
    #run_file()
    #run_dir()
    run_webcam()

