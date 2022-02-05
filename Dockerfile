### 以 python 来作为基础镜像
FROM python:latest
### 创建工作目录
### 将 python 项目复制到工作目录下
COPY . /
### 设置工作目录
WORKDIR /

### 安装 ffmpeg
COPY ./sources.list /etc/apt/sources.list
RUN DEBIAN_FRONTEND=noninteractive apt update -y
RUN DEBIAN_FRONTEND=noninteractive apt install ffmpeg -y

### 下载 python 项目的依赖库
# RUN python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
### 在创建个爬取的数据存放的目录，这个需要根据自己代码里面设置的目录来创建，例如：
### VOLUME /data
### 最后一步，运行docker镜像时运行自己的python项目
### 可以多个参数： CMD ["python3","a","main.py"]
ENTRYPOINT ["python3"]
# CMD ["src/main.py", "/movies", "rtmp://tx.direct.huya.com/huyalive/316197277-316197277-0-632518010-10057-A-1643620300-1?seq=1643620302131&type=simple"]
CMD ["src/main.py"]