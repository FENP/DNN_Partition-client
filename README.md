

## 环境搭建（客户端与服务端基本相同）

### 1. 创建pytorch环境

可以根据需要安装CPU或GPU版本的pytorch[参考这里](https://pytorch.org/get-started/locally/)

下面是使用conda安装GPU版本pytorch的代码

```shell
# 创建pytorch虚拟环境
conda create -n pytorch python=3.8
conda activate pytorch
# 安装pytorch的GPU版本
conda install pytorch cudatoolkit=10.2
```

### 2. 安装python包

```shell
# 安装thrift pandas PIL torchvision
conda install thrift pandas Pillow torchvision
```

### 3. 安装Thrift的IDL编译工具

```shell
# 安装编译thrift所需的工具
sudo apt install cmake flex bison
# clone thrift
git clone https://github.com/apache/thrift.git
# 编译thrift
cd thrift/compiler/cpp
mkdir cmake-build
cd cmake-build
cmake ..
make
# 添加环境变量
export PATH=~/thrift/compiler/cpp/cmake-build/bin:$PATH
# 检查是否成功
thrift -version
```

## 克隆项目

辅助工具的使用参见相应项目的README文档

```shell
# 客户端代码
git clone https://github.com/FENP/DNN_Partition-client.git
# 辅助工具
git clone https://github.com/FENP/pytorchtool.git
```

## 编译thrift文件

编译输出的python包`dnnpartition`与`DNN_Partition-client`在同一目录下

```shell
cd ./DNN_Partition-client
thrift -out .. --gen py ./thrift_file/dnnpartition.thrift
```

## 获取模型各层参数

使用pytorchtool对模型各层进行分析，将服务端的结果与客户端结果整合，Loading Time为服务端的各层初始化时间、Execute Time Server为服务端各层执行时间。具体可参考pytorchtool中`./parameters`目录下的csv文件。

## 获取模型DAG结构

目前没有找到好的方法，只能自己写dag文件，参考pytorchtool中`./parameters`目录下的dag文件

## 运行客户端

服务端启动后运行`python client.py`