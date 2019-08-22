# 基于百度地图API的个人信息模糊匹配
GSK_Intern_2,共计四个文档，以下将分别叙述




## 目录

* [主要功能](#主要功能)
* [使用及运行](#使用及运行)
* [样例及结果](#样例及结果)
* [详细入口参数及使用方法](#详细入口参数及使用方法)
* [其余方法说明](#其余方法说明)
* [Oracle写回、改进及维护](#Oracle写回、改进及维护)
* [文件说明](#文件说明)
* [写在最后](#写在最后)


## 主要功能
本程序针对专项字符串——医院名称进行模糊匹配，涉及包含关系，关键字查找，地图api匹配等模式

## 使用及运行

- 运行本程序必须安装的模块有：cx_Oracle，xlsxwriter，pandas，time，json，urllib.request，geopy.distance等
- geopy**仅支持python3**
- **为了获得好的效果和速度，建议通过[**requirements.txt**](https://github.com/yingjiaxuan/Intern_2_public/blob/master/requirements.txt)文件完成环境匹配**

    

1. 通过requirements.txt安装：
	```
	pip install -r requirements.txt
	```
	以上为你自己的requirements.txt路径
	
2. 如果不希望影响自己已有的python环境，可以通过官方镜像逐条安装，比如：   
   初次安装：
	```
	pip install cx_Oracle
	```
   
3. 如果使用pip方法安装某个包时产生问题，建议通过[**官方包库**](https://www.lfd.uci.edu/~gohlke/pythonlibs/#python-ldap)手动下载：
    
    比如下载安装geopy库时产生问题，则从在包库页面输入Ctrl+F,搜索到对应包，下载并放入python环境Scripsts文件夹内，然后在python终端输入
	```
	pip install C:\ProgramData\Anaconda3\Scripts\geopy-1.20.0-py2.py3-none-any.whl
	```
	其中，路径应为您自己的路径地址
	

注意：**geopy包目前及以后都支持python3版本**

建议：推荐使用[**pycharm**](https://www.jetbrains.com/pycharm/download/#section=windows)作为编译器，同时使用[**Anaconda**](https://www.anaconda.com/)包管理器用以包管理



## 样例及结果
以下选择7组典型原数据展示标注结果：

| Hos_Source | Hos_Preference | 信度分析 |
| :-----: | :--------: | :-----: |
|   北京市门头沟区医院  |     北京市门头沟区医院 |  1 |
| 青海红十字医院 |    青海省西宁市红十字会医院（青海红十字医院）|  2 |
| 厦门市第二医院 |    福建省厦门医学院附属第二医院|  3 |
| 赣州市第五人民医院 |    江西省赣州市肺科医院|  4 |
| 武侯区第三人民医院 |    四川省成都市武侯区第五人民医院|  -1 |
| 中国人民解放军总医院301医院 |    空军航空医学研究所附属医院|  -2 |
| 包钢医院 |    内蒙古包头市蒙医中医医院|  0 |

其中信度标签意义如下：

| **编号** | *意义* | 
| :-----: | :-------- | 
|1|字符串完全一致|
|2|字符串为互相包含关系|
|3|字符串通过“第X医院”逻辑确定为同一所|
|4|字符串通过坐标匹配在1km以内，认定为同一所|
|-1|字符串通过“第X医院”逻辑确定不是同一所|
|-2|字符串通过坐标匹配在1km以外，认定不是同一所|
|0|字符串在1,2,3匹配均无结果，在4匹配时产生无返回值现象，无法认定|

## 详细入口参数及使用方法

### 一、入口参数获取——来源于Oracle数据库
根据数据源创建视图——名字相同，省市除后缀（省、市）以外相同，即问题最终聚焦在医院是否为同一所
```sql
CREATE VIEW v4(SOURCE_NAME,reference_province,reference_city,source_hospital,REFERENCE_HOSPITAL) AS
SELECT source.hcp_name,reference.province,reference.city,source.hco_name,reference.name
    FROM source,reference 
    where reference.hcp_name = source.hcp_name 
    and instr(source.province_name,reference.province)>0 
    and instr(source.city_name,reference.city)>0 
    order by source.hcp_name;
```

### 二、代码解析——基于文件[Create_view.py](https://github.com/yingjiaxuan/GSK_Intern_Module_2/blob/master/Create_view.py),[Check_Hos.py](https://github.com/yingjiaxuan/GSK_Intern_Module_2/blob/master/Check_Hos.py),[Fun_3](https://github.com/yingjiaxuan/GSK_Intern_Module_2/blob/master/Fun_3.py),[Folium.py](https://github.com/yingjiaxuan/GSK_Intern_Module_2/blob/master/Folium.py)
以下代码示例适用于python交互式环境及pycharm编译器。

#### 1.生成视图映射表（Create_view.py 36-47行）

应用时修改实际使用的数据库usr_name,pwd,dsn以及实际写入目标文件路径，生成文件行列信息参考上方链接
```python
user_name = '123'
password = '123123'
dsn_tst = cx_Oracle.makedsn('url', '1111', 'AAAA') # 基本信息

sql = "select * from v4" # 具体视图名称
sql_list = get_sql_list(user_name,password,dsn_tst,sql)

# ***********************写入文件模块*******************************
workbook_goal = xlsxwriter.Workbook('C:\Personal_File\DiskF\GSK_Intern_Oracle\Tem_file\SQL_TEM_1.xlsx')
worksheet = workbook_goal.add_worksheet()
```
#### 2.基于映射表添加信度标签行（Check_Hos.py）

应用时修改为自己的源文件及目标文件路径（图省事可以直接通过ExcelGUI修改）
```python
t = 'root_1'
t_2 = 'root_2'
df = pd.read_excel(t, sheet_name="Sheet1")

row_num, column_num = df.shape
df['信度分析'] = None
for row_loop in range(row_num):
    df.iloc[row_loop,df.shape[1]-1] = 0

df.to_excel(t_2, sheet_name='Sheet1', index=False, header=True)
print('Finish_Processing')
```
#### 3.字符串处理主方法（Fun_3.py）——由于为主方法，各子方法前额外添加所需要的包
##### 3.1 fun_Simple_Processor

进行简单逻辑匹配——完全一致，包含关系，“第x医院”逻辑匹配，返回值参考上文

由于逻辑相对简单，此处不放完整子方法代码，需要的可以点击[链接](https://github.com/yingjiaxuan/GSK_Intern_Module_2/blob/master/Fun_3.py)查看，或参考后文[其余方法说明](#其余方法说明)
```python
def fun_Simple_Processor(t_1, t_2):
    t_1 = func_Delete_Comma(t_1) 
    t_2 = func_Delete_Comma(t_2)
    if t_1 == t_2:  # 占据11.85%，5456个
        return 1
    if fun_Check_Num(t_1, t_2) == True:  # 占据16.85%，7754个
        return 3
    if fun_Check_Num(t_1, t_2) == False:  # 占据2.05%，943个
        return -1
    list_1 = func_str_to_list(t_1)
    list_2 = func_str_to_list(t_2)
    bool = fun_Set_Processor(list_1, list_2)
    if bool == True:
        return 2  # 占据40.12%，18467个 ——》添加“第*”判断后，占据25.52%，11748个
    return 0
```

##### 3.2 fun_Coordinate_Processor和getlnglat

getlnglat(address)为api主方法，使用时，应当填入企业ak，其余参数均不需要修改

企业ak申请方法请参考[这个链接](http://lbsyun.baidu.com/index.php?title=webapi/guide/webservice-geocoding)
```python
from urllib.request import urlopen, quote
from geopy.distance import geodesic
import json
def getlnglat(address):
    url = 'http://api.map.baidu.com/geocoding/v3/'
    output = 'json'
    ak = 'ak'  # 应用时改为企业ak，其余都不需要修改
    add = quote(address)  # 由于本文城市变量为中文，为防止乱码，先用quote进行编码
    uri = url + '?' + 'address=' + add + '&output=' + output + '&ak=' + ak
    req = urlopen(uri)
    res = req.read().decode()  # 将其他编码的字符串解码成unicode
    temp = json.loads(res)  # 对json数据进行解析
    if temp['status'] != 0:
        return temp['status'],None
    lng = temp['result']['location']['lng']
    lat = temp['result']['location']['lat']  # 纬度——latitude,经度——longitude
    return lat, lng
```

```python
from geopy.distance import geodesic
def fun_Coordinate_Processor(t_1,t_2):
    tuple_1 = getlnglat(t_1)
    tuple_2 = getlnglat(t_2)
    if tuple_1[1] == None or tuple_2[1]==None:
        return 0
    distance = geodesic(tuple_1, tuple_2).km
    if distance > 1:
        return -2
    else:
        return 4
```
#### 4.生成匹配成功数据源可视化地图（Folium.py）

使用时，修改源文件路径，其余均不需要修改，生成文件可参考[**df.html**](https://github.com/yingjiaxuan/GSK_Intern_Module_2/blob/master/df.html)
```python
import pandas as pd
import cpca
from cpca import drawer
t = 'root' # 文件路径
df = pd.read_excel(t, sheet_name="Sheet1")
row_num, column_num = df.shape

text=[]
for row_loop in range(row_num):
    t_1 = df.loc[row_loop, '信度分析']
    t_2 = df.loc[row_loop, 'Province_From_Preference']
    t_3 = df.loc[row_loop, 'City_From_Preference']
    if t_1 >0:
        tem_t = str(t_2) + str(t_3)
        text.append(tem_t)

df_map = cpca.transform(text)
drawer.draw_locations(df_map, "df.html")
```

## 其余方法说明
### 1.func_Delete_Comma

去除字符以外的全部符号，入口参数为字符串，出口参数为处理后的字符串
```python
import re
def func_Delete_Comma(line):
    rule = re.compile(r"[^a-zA-Z0-9\u4e00-\u9fa5]")
    line = rule.sub('', line)
    return line
```
### 2.print_time
于程序各节点计时，可用于测试优化，其中time_1为全局变量
```python
import time
def print_time():
    global time_1
    tem_t = time.time()
    tem = tem_t - time_1
    z = round(tem, 3)
    print("累计消耗时间为:" + str(z))

time_1 = time.time()
```
### 3.func_str_to_list

字符串拆成单个字符，并忽略“省”“市”“区”
```python
def func_str_to_list(line):
    list = []
    for tem in line:
        if tem != '省' and tem != '市' and tem != '区':
            list.append(tem)
    return list
```
### 4.fun_Set_Processor
将list转换为set并进行包含关系判断
```python
def fun_Set_Processor(list_1, list_2):
    if len(list_1) >= len(list_2):
        A = set(list_1)
        B = set(list_2)
    else:
        A = set(list_2)
        B = set(list_1)
    return B <= A
```
### 5.fun_Check_Num
对字符串进行“第x医院”逻辑判断
```python
import re
def fun_Check_Num(t_1, t_2):
    n_1 = re.search(r'第[一二三四五六七八九]', t_1)
    n_2 = re.search(r'第[一二三四五六七八九]', t_2)
    if n_1 == None or n_2 == None:
        return 1234
    if n_1.group(0) == n_2.group(0):
        return True
    else:
        return False
```

## Oracle写回、改进及维护
### 1. Oracle写回
考虑到[样例输出](https://github.com/yingjiaxuan/GSK_Intern_Module_2/blob/master/Output_Demo.xlsx)尚需要对精度做出讨论，暂未实现Oracle写回脚本，暂定利用Dual虚表进行批量写回
### 2. 改进
针对[Fun_3.py](https://github.com/yingjiaxuan/GSK_Intern_Module_2/blob/master/Fun_3.py)中的坐标判断，仍可以通过规定距离值，设置梯度信度作二次校验等方法进一步提高匹配准确率
### 3. 维护
不建议修改除文件路径，ak以外的任何内容，以免造成不可估计的逻辑错误

## 文件说明
1. [Check_Hos.py](https://github.com/yingjiaxuan/Intern_2_public/blob/master/Check_Hos.py)
根据视图生成对应Excel文档（具有生成耦合）
2. [Create_View.py](https://github.com/yingjiaxuan/GSK_Intern_Module_2/blob/master/Create_view.py)
根据生成的Excel文档添加额外的信度列（此处开始只与前者生成的文档具有耦合，与原数据已脱钩）
3. [Fun_3.py](https://github.com/yingjiaxuan/GSK_Intern_Module_2/blob/master/Fun_3.py)
字符串匹配处理主方法
4. [Folium.py](https://github.com/yingjiaxuan/GSK_Intern_Module_2/blob/master/Folium.py)
根据匹配结果生成匹配热点图
5. [SQL_TEM_1.xlsx](https://github.com/yingjiaxuan/GSK_Intern_Module_2/blob/master/SQL_TEM_1.xlsx)
对应视图生成的Excel文档
6. [Output_Demo.xlsx](https://github.com/yingjiaxuan/GSK_Intern_Module_2/blob/master/Output_Demo.xlsx)
生成完毕信度标签的Excel文档
7. [df.html](https://github.com/yingjiaxuan/GSK_Intern_Module_2/blob/master/df.html)
生成的匹配热点图
8. [requirements.txt](https://github.com/yingjiaxuan/GSK_Intern_Module_2/blob/master/requirements.txt)
环境配置文件

## 写在最后
有任何关于本程序的问题及建议，欢迎将邮件发至：[*yingjiaxuan123@163.com*](link)















