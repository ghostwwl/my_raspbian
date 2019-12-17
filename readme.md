
# 树莓派4b相关记录

## 目录
<ol>
	<li><a href="#常用库安装">常用库安装</a></li>
    <li><a href="#开启开机无显示器 `SSHD` 登录">开启开机无显示器 `SSHD` 登录</a></li>
    <li><a href="#无线网络相关">无线网络相关</a></li>
    <li><a href="#安装 `tensorflowlite-bin` 或者 `tensorflow`">安装 `tensorflowlite-bin` 或者 `tensorflow`</a></li>
    <li><a href="#安装 sambda 当简单的 nas">安装 sambda 当简单的 nas</a></li>
    <li><a href="#安装 minidlna 当 dlna 服务器">安装 minidlna 当 dlna 服务器</a></li>
    <li><a href="#配置自己的服务，所有systemd启动的linux 都能这么干">配置自己的服务，所有systemd启动的linux 都能这么干</a></li>
    <li><a href="#树莓派系统备份及恢复">树莓派系统备份及恢复</a></li>
</ol>


## 常用库安装
```

# 安装中文字字体
sudo apt-get install ttf-wqy-zenhei ttf-wqy-microhei

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


```

## 开启开机无显示器 `SSHD` 登录

- 树莓派4b 默认是不开启sshd登录的， 以前版本的是默认开启的
- 开启方法
    - 系统boot目录 `touch SSH`
- 配置自动连接wifi配置文件
    - 系统boot目录新建一个wpa_supplicant.conf文件内容如下：
        - ssid:网络的ssid
        - psk:密码
        - priority:连接优先级，数字越大优先级越高（不可以是负数）
        - scan_ssid:连接隐藏WiFi时需要指定该值为1

```
            
            country=CN
            ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
            
            update_config=1
            network={
                ssid="WiFi-A"
                psk="12345678"
                key_mgmt=WPA-PSK
                priority=1
            }
            
            
```


----------------------

## 无线网络相关

### 查看网络状态
- 命令`sudo iw dev wlan0 info`
- 要获取station 的统计信息，如发送/接收的字节，最后发送的比特率（包括MCS率）
> sudo iw dev wlan0 station dump

### 扫描无线网络
- 运行 `sudo iw dev wlan0 scan`
- 只看SSID `sudo iw dev wlan0 scan|grep 'SSID'`



----------------------


## 安装 `tensorflowlite-bin` 或者 `tensorflow`

- [https://github.com/PINTO0309/TensorflowLite-bin](https://github.com/PINTO0309/TensorflowLite-bin)
- [https://github.com/PINTO0309/Tensorflow-bin](https://github.com/PINTO0309/Tensorflow-bin)
- [https://www.tensorflow.org/lite/guide/hosted_models](https://www.tensorflow.org/lite/guide/hosted_models)


## 安装 `pytorch`

- 自动安装好 torchvision + pytorch
> sudo pip3 install torchvision-raspi



## 安装 sambda 当简单的 nas

```
apt install samba samba-common-bin
```

- 把 `/home/pi` 共享出去 修改 `/etc/samba/smb.conf` 底下增加

```
        [public]
            # 说明信息
            comment = public storage
            # 共享文件的路径
            path = /home/pi
            # 可以访问的用户
            valid users = @pi
            force group = users
            # 新建文件权限
            create mask = 0660
            # 新建目录权限
            directory mask = 0771


```

- 把 `[homes]` 下对应的 改为 `read only = no`
- 添加 sambda 用户
> smbpasswd -a pi

- 启动 `/etc/init.d/smbd start` 或 `sudo systemctl start smbd.service`
- 禁止开机自启动 `sudo systemctl disable smbd.service`


## 安装 minidlna 当 dlna 服务器
- 执行 `sudo apt-get install minidlna`
- 编辑 `vim /etc/minidlna.conf` 加入

```
    media_dir=A,/home/pi/dlna/Music
    media_dir=P,/home/pi/dlna/Picture
    media_dir=V,/home/pi/dlna/Video
    db_dir=/home/pi/dlna/db
    log_dir=/home/pi/dlna/log


```

- 停止服务 `sudo systemctl stop minidlna.service`
- 禁止开机启动 `sudo systemctl disable minidlna.service`

- 启动和停止 我是这么搞的 `vim dlna.sh`

```
    #!/bin/sh
    
    
    function_start_dlna()
    {
    	printf "Starting MiniDlna...\n"
    	minidlnad -f /etc/minidlna.conf -P /home/pi/dlna/minidlna.pid -r -L
    }
    
    function_stop_dlna()
    {
    	printf "Stoping MiniDlna...\n"
    	if [ -f /home/pi/dlna/minidlna.pid ] ; then
    		kill -15 `cat /home/pi/dlna/minidlna.pid`
    	else
    		kill -15 $(ps -ef|grep 'minidlnad'|grep -v 'grep'|awk '{printf $2}')
    	fi
    }
    
    if [ "$1" = "start" ]; then
    	function_start_dlna
    elif [ "$1" = "stop" ]; then
    	function_stop_dlna
    elif [ "$1" = "restart" ]; then
    	function_stop_dlna
    	function_start_dlna
    else
    	printf "Usage: dlna.sh {start|stop|restart}\n"
    fi

```


----------------------


## 配置自己的服务，所有systemd启动的linux 都能这么干

### 一、Systemd简介
Systemd是由红帽公司的一名叫做Lennart Poettering的员工开发，systemd是Linux系统中最新的初始化系统（init）,它主要的设计目的是克服Sys V 固有的缺点，提高系统的启动速度，systemd和upstart是竞争对手，ubantu上使用的是upstart的启动方式，centos7上使用systemd替换了Sys V，Systemd目录是要取代Unix时代依赖一直在使用的init系统，兼容SysV和LSB的启动脚本，而且能够在进程启动中更有效地引导加载服务。
system：系统启动和服务器守护进程管理器，负责在系统启动或运行时，激活系统资源，服务器进程和其他进程，根据管理，字母d是守护进程（daemon）的缩写，systemd这个名字的含义就是它要守护整个系统。

### 二、Systemd新特性
- 系统引导时实现服务并行启动
- 按需启动守护进程
- 自动化的服务依赖关系管理
- 同时采用socket式与D-Bus总线式激活服务
- 系统状态快照和恢复
- 利用Linux的cgroups监视进程
- 维护挂载点和自动挂载点
- 各服务间基于依赖关系进行精密控制

### 三、Systemd核心概念

- Unit  
表示不同类型的sytemd对象，通过配置文件进行标识和配置，文件中主要包含了系统服务，监听socket、保存的系统快照以及其他与init相关的信息

- 配置文件:  
/usr/lib/systemd/system：每个服务最主要的启动脚本设置，类似于之前的/etc/initd.d
/run/system/system：系统执行过程中所产生的服务脚本，比上面的目录优先运行
/etc/system/system：管理员建立的执行脚本，类似于/etc/rc.d/rcN.d/Sxx类的功能，比上面目录优先运行，在三者之中，此目录优先级最高

### 四、Systemd基本工具
监视和控制systemd的主要命令是systemctl。该命令可用于查看系统状态和管理系统及服务。

- 管理服务
    - 命令：systemctl  command name.service
    - 启动：service name start –>systemctl start name.service
    - 停止：service name stop –>systemctl stop name.service
    - 重启：service name restart–>systemctl restart name.service
    - 状态：service name status–>systemctl status name.service

- 条件式重启(已启动才重启，否则不做任何操作)
    - `systemctl try-restart name.service`

- 重载或重启服务(先加载，然后再启动)
    - `systemctl reload-or-try-restart name.service`

- 禁止自动和手动启动
    - `systemctl mask name.service`  --> 执行此条命令实则创建了一个链接 ln -s '/dev/null' '/etc/systemd/system/sshd.service'

- 取消禁止
    - `systemctl unmask name.service`  --> 删除此前创建的链接

- 服务查看(查看某服务当前激活与否的状态)
    - `systemctl is-active name.service`  -->  如果启动会显示active，否则会显示unknown

- 查看所有已经激活的服务
    - `systemctl list-unit-files -t service|awk '$2 ~/enabled/'`

- 查看所有服务
    - `systemctl list-unit-files`

- 设定某服务开机启动
    - `systemctl enable name.service`

- 设定某服务开机禁止启动
    - `systemctl disable name.service`

- 查看所有服务的开机自启状态
    - `systemctl list-unit-files -t service`

- 用来列出该服务在那些运行级别下启用或禁用
    - 比喻sshd: `ls /etc/systemd/system/*.wants/sshd.service`

- 查看服务是否开机自启
    - `systemctl is-enabled name.servcice`

- 查看服务的依赖关系
    - `systemctl list-dependencies`

- 查看启动失败的服务
    - `systemctl -failed -t service`

- 查看服务单元的启用和禁用状态


- 杀死进程
    - systemctl kill 进程名

- 服务状态
    - `systemctl list-units -t service -a 显示状态`
        - loaded：unit配置文件已处理
        - active（running）：一次或多次持续处理的运行
        - active（exited）：成功完成一次性的配置
        - active（waiting）:运行中，等待一个事件
        - inactive：不运行
        - enabled：开机启动
        - disabled：开机不启动
        - static：开机不启动，但可以被另一个启用的服务激活

- 查看默认运行级别 
    - `systemctl get-default`

- 级别切换
    - `systemctl isolate muti-user.target`
    -  注意：只有当/lib/systemd/system/*.target文件中AllowIsolate=yes时才能奇幻（修改文件需执行systemctl daemon-reload生效）
        -  `grep 'AllowIsolate=yes' /lib/systemd/system/*.target`


### 五、配置我们自己的代码为运行服务

- 假设我们要运行的代码在`/home/pi/mycode.py` 
- 编辑 `/lib/systemd/system/mycode.service` 文件

```
        [Unit]
        Description=MyCode Service
        After=multi-user.target
        
        [Service]
        Type=idle
        ExecStart=/usr/bin/python3 /home/pi/mycode.py
        
        [Install]
        WantedBy=multi-user.target

```

- 为了将脚本的文本输出存储在日志文件中，您可以将ExecStart行更改为：
> ExecStart=/usr/bin/python3 /home/pi/mycode.py > /home/pi/mycode.log 2>&1
- 需要将单元文件上的权限设置为644，如： 
> sudo chmod 644 /lib/systemd/system/mycode.service
- 配置systemd，systemd在引导序列中启动它
> sudo systemctl daemon-reload
> sudo systemctl enable mycode.service
- 重启树莓派
> sudo reboot
- 检查服务状态
> sudo systemctl status mycode.service




----------------------

## 树莓派系统备份及恢复
### 为什么要这么干?
1. 老系统装东西太多 要试新系统 只有一个卡呢
    - 备份老的
    - 装新的完 玩坏也不怕
2. 多个 pi 量产啊 要相同的预装软件
    - 预装好系统和app 搞好后做镜像
    - 再用镜像去做一堆tf卡量产

### 备份树莓派tf卡到镜像
- 把卡放到读卡器 插入linux系统的电脑
- 通过`sudo fdisk -l` 找到设备文件 不要`mount` 我的是`/dev/sdb`
- 备份到一个地方 我的是 /home/ghostwwl/myraspi
    > sudo dd if=/dev/sdb of=/home/ghostwwl/myraspi/rpi_2019.11.27_backup.img bs=4M conv=sync status=progress

### 恢复到tf卡
- 假设usb读卡器设备是 `/dev/sdb` 先 `sudo fdisk -l` 看下 不要`mount`
> sudo dd if=/home/ghostwwl/myraspi/rpi_2019.11.27_backup.img of=/dev/sdb bs=4M conv=sync status=progress
- 如果恢复的目标sd卡 比原始的大小不一致 按照下面的操作 使用整个卡空间
    1. 把恢复完的卡插入树莓派启动
    2. 执行 `sudo raspi-config`
    3. 选择 `Advanced ...` 这个
    4. 然后选择 `A1 Expand FileSystem....`  操作完 重启ok


----------------------


## 摄像头相关
- 我用的是usb的罗技c920
    - 直接插在usb 3.0口
    - 运行 `lsusb` 可以看到类似 `Bus 001 Device 003: ID 046d:082d Logitech, Inc. HD Pro Webcam C920`
    - 拍照`sudo fswebcam -s -no-banner -r 800*600 image.jpg`

- 安装 motion 作为监控
    - 貌似可以配置检测到画面移动时 录制视频的
    - 更改 `stream_localhost on` --> off
    - 更改 `webcontrol_localhost on` --> off
    - 同局域网访问 'http://xxxx:8081' 可以看到图像
        
- 安装相关软件

```
$ sudo apt-get install libjpeg8-dev
$ sudo apt-get install imagemagick
$ sudo apt-get install libv4l-dev
$ sudo apt-get install subversion

sudo ln -s /usr/include/libv4l1-videodev.h /usr/include/linux/videodev.h
sudo ln -s /usr/include/linux/videodev2.h /usr/include/linux/videodev.h

$ svn co http://svn.code.sf.net/p/mjpg-streamer/code/  mjpg-streamer-code-182
$ cd mjpg-streamer-code-182/mjpg-streamer
& sudo make USE_LIBV4L2=true clean all
$ sudo make DESTDIR=/usr install

```


## 安装放歌的 xmms2 
- `sudo apt-get install xmms2`


