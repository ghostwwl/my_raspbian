#!/bin/sh


# 安装build-essential、cmake、git和pkg-config
sudo apt-get install build-essential cmake git pkg-config

# 安装优化函数包
sudo apt-get install libatlas-base-dev gfortran

# 安装jpeg格式图像工具包
sudo apt-get install libjpeg8-dev

# 安装tif格式图像工具包
sudo apt-get install libtiff5-dev

# 安装JPEG-2000图像工具包
sudo apt-get install libjasper-dev

# 安装png图像工具包
sudo apt-get install libpng12-dev

sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev

# 安装gtk2.0
sudo apt-get install libgtk2.0-dev

# 安装的Raspbian系统自带Python编译器，若没有安装，执行下列命令进行安装
sudo apt-get install python-dev python3-dev
sudo apt install swig libjpeg-dev zlib1g-dev python3-numpy unzip


# 安装中文字字体
sudo apt-get install ttf-wqy-zenhei ttf-wqy-microhei

# 升级固件
sudo rpi-update
sudo apt dist-upgrade

# 系统升级
sudo apt-get update
sudo upgrade

# 网络相关工具
sudo apt-get install atop htop nethogs iptraf bmon

# 安装tensorflow
sudo apt-get install -y libhdf5-dev libc-ares-dev libeigen3-dev
sudo pip3 install keras_applications==1.0.8 --no-deps
sudo pip3 install keras_preprocessing==1.1.0 --no-deps
sudo pip3 install h5py==2.9.0
sudo apt-get install -y openmpi-bin libopenmpi-dev
sudo apt-get install -y libatlas-base-dev
sudo pip3 install -U six wheel mock
sudo sudo pip3 uninstall tensorflow
wget https://github.com/PINTO0309/Tensorflow-bin/raw/master/tensorflow-1.15.0-cp37-cp37m-linux_armv7l.whl
sudo pip3 install tensorflow-1.15.0-cp37-cp37m-linux_armv7l.whl

# 安装tensorflowlite-bin
wget https://github.com/PINTO0309/TensorflowLite-bin/raw/master/1.15.0/tflite_runtime-1.15.0-cp37-cp37m-linux_armv7l.whl
sudo pip3 install --upgrade tflite_runtime-1.15.0-cp37-cp37m-linux_armv7l.whl

# 安装pytorch
sudo pip3 install torchvision-raspi

# 安装selenium
sudo apt install chromium-browser chromium-chromedriver
pip3 install selenium
