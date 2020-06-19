# 一、项目总览

## 1、技术栈

- Vue——前端开发框架
- Django——后端开发框架
- Scrapy——爬虫框架
- Ant Design——UI框架
- Pyecharts——制图

## 2、功能

### 1）爬虫

- 爬取链家租房信息
- 爬取蛋壳公寓租房信息
- 使用代理池容错

### 2）Web后端

- 登录校验

- 根据token获取用户信息

- 获取租房数据

- 删除租房数据

- 获取代理池数据

- 获取代理池总数

- 删除指定代理

- 根据需求使用pyecharts制作并返回各种图表的json序列化格式

### 3）Web前端

- 登录验证

- 实现登录界面

- 实现数据总览界面，提供筛选、排序、分页的功能

- 实现数据可视化界面，提供基本情况分析（包含平均租金分析、租赁方式及类型分析以及标签分析）、区域分析（包含热力图分析、饼图分析）以及价格分析（包含价格分布分析、性价比分析、各小区单位面积租金分析）功能；

- 实现代理池的展示功能（包含代理池数据的展示、统计可用代理数以及删除指定代理的功能）。

## 3、体系结构

![体系结构](https://github.com/PanZ12580/Renting/tree/master/markdown_images\项目结构.png)

## 4、运行效果

### 1）登录界面

![image-20200618031405046](https://github.com/PanZ12580/Renting/tree/master/markdown_images\image-20200618031405046.png)

### 2）数据总览界面

![数据总览界面](https://github.com/PanZ12580/Renting/tree/master/markdown_images\数据总览界面.png)

### 3）基本情况分析

![基本情况分析](https://github.com/PanZ12580/Renting/tree/master/markdown_images\基本情况分析.png)

![基本情况分析2](https://github.com/PanZ12580/Renting/tree/master/markdown_images\基本情况分析2.png)

### 4）区域分析

这里需要用到百度地图的api，需要申请AK，项目中我把我申请的一个AK放上去了，位置在：

Vue项目中的index.html：

![image-20200619120857758](https://github.com/PanZ12580/Renting/tree/master/markdown_images\image-20200619120857758.png)

Django项目中App中的views.py：

![image-20200619121008956](https://github.com/PanZ12580/Renting/tree/master/markdown_images\image-20200619121008956.png)

以后可能会失效，请自行更换

![区域分析1](https://github.com/PanZ12580/Renting/tree/master/markdown_images\区域分析1.png)

![区域分析2](https://github.com/PanZ12580/Renting/tree/master/markdown_images\区域分析2.png)

### 5）价格分析

![价格分析1](https://github.com/PanZ12580/Renting/tree/master/markdown_images\价格分析1.png)

![价格分析2](https://github.com/PanZ12580/Renting/tree/master/markdown_images\价格分析2.png)

![价格分析3](https://github.com/PanZ12580/Renting/tree/master/markdown_images\价格分析3.png)

# 二、Django项目

Django是我两天速成的。。。。大佬们看个笑话就好了。

进入目录：

![image-20200618031046997](https://github.com/PanZ12580/Renting/tree/master/markdown_images\image-20200618031046997.png)

首先需要导入数据库文件，直接通过

```
python manage.py makemigrations
python manage.py migrate
```

进行数据库迁移也可以，不过得到的数据库都是空的。

导入sql文件的方式有多种，比如使用source命令导入：

```mysql
mysql> create database renting CHARACTER SET 'utf8' COLLATE 'utf8_general_ci';      # 创建数据库,设置编码
mysql> use renting;                  # 使用已创建的数据库 
mysql> set names utf8;           # 设置编码
mysql> source 目录路径/renting.sql  # 导入备份数据库
```

也可以通过可视化界面如SQLyog来导入

然后执行pip命令安装项目依赖：

```
pip install -r requirements.txt
```

接下来，在django中配置数据库连接的参数：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'renting',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': '127.0.0.1',
        'PORT': 3306
    }
}
```

然后通过以下命令生成模型。

```powershell
python manage.py inspectdb > models.py
```

之后会得到一个models.py文件，将其中的`managed=False`参数删除，让django托管这些表，同时还可选择重写`__str__(self)`方法来定义输出格式。

启动项目：

```
py manage.py runserver 8000
```

在8000端口启动项目，然后在浏览器访问<http://127.0.0.1:8000>地址，就可以进入项目了：

![image-20200618031405046](https://github.com/PanZ12580/Renting/tree/master/markdown_images\image-20200618031405046.png)

数据库中默认有可供登录的账号为：

```
id	username	password
1	admin		123456
```

# 三、Scrapy项目

在运行Scrapy项目之前，由于其用到了代理池，所以先确保代理池是启动状态，进入`代理池\ProxyPool`文件中，运行其中的`run.py`脚本启动好代理池。

其次还好保证上一步中的数据库及表已创建好。

进入Scrapy项目中：

![image-20200618032037788](https://github.com/PanZ12580/Renting/tree/master/markdown_images\image-20200618032037788.png)

文件夹中有两个scrapy项目，首先安装好依赖：

```
pip install -r requirements.txt
```

然后分别进入到两个爬虫项目中：

![image-20200618032131505](https://github.com/PanZ12580/Renting/tree/master/markdown_images\image-20200618032131505.png)

运行其中的running.py脚本即可。

注意，运行前请先进入到项目中的项目文件夹中，打开`pipelines.py`文件，查看其数据库连接参数与自己机器上的是否一致：

![image-20200618032801620](https://github.com/PanZ12580/Renting/tree/master/markdown_images\image-20200618032801620.png)

# 四、VUE项目（可选）

Vue的项目已经打包部署到Django环境中了，只是想让项目跑起来的话这一步可以不用做。

需要node环境，可直接到官网下载安装。

进入到Vue项目中：

![image-20200618031523065](https://github.com/PanZ12580/Renting/tree/master/markdown_images\image-20200618031523065.png)

安装依赖

```
npm install
```

运行项目

```
npm run serve
```

打包

```
npm run build
```