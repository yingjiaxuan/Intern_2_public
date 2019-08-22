import pandas as pd
import time
import re
import json
from urllib.request import urlopen, quote
from geopy.distance import geodesic


def print_time():
    global time_1
    tem_t = time.time()
    tem = tem_t - time_1
    z = round(tem, 3)
    print("累计消耗时间为:" + str(z))


time_1 = time.time()


# 去除字符以外的全部符号
def func_Delete_Comma(line):
    rule = re.compile(r"[^a-zA-Z0-9\u4e00-\u9fa5]")
    line = rule.sub('', line)
    return line


# 字符串拆分成单个字符
def func_str_to_list(line):
    list = []
    for tem in line:
        if tem != '省' and tem != '市' and tem != '区':
            list.append(tem)
    return list


t = 'root'
df = pd.read_excel(t, sheet_name="Sheet1")
row_num, column_num = df.shape
print_time()


# ***************************所有操作写在下面****************************
# list转换为set进行子集分析
def fun_Set_Processor(list_1, list_2):
    if len(list_1) >= len(list_2):
        A = set(list_1)
        B = set(list_2)
    else:
        A = set(list_2)
        B = set(list_1)
    return B <= A


def fun_Check_Num(t_1, t_2):
    n_1 = re.search(r'第[一二三四五六七八九]', t_1)
    n_2 = re.search(r'第[一二三四五六七八九]', t_2)
    if n_1 == None or n_2 == None:
        return 1234
    if n_1.group(0) == n_2.group(0):
        return True
    else:
        return False


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
        return temp['status'], None
    lng = temp['result']['location']['lng']
    lat = temp['result']['location']['lat']  # 纬度——latitude,经度——longitude
    return lat, lng


def fun_Coordinate_Processor(t_1, t_2):
    tuple_1 = getlnglat(t_1)
    tuple_2 = getlnglat(t_2)
    if tuple_1[1] == None or tuple_2[1] == None:
        return 0
    distance = geodesic(tuple_1, tuple_2).km
    if distance > 5:
        return -2
    else:
        return 4


def fun_Coordinate_Processor_another(t_1, t_2):
    tuple_1 = getlnglat(t_1)
    tuple_2 = getlnglat(t_2)
    if tuple_1[1] == None or tuple_2[1] == None:
        return 0
    distance = geodesic(tuple_1, tuple_2).km
    return distance


# 处理字符串主函数1
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


i = 0
j = 0
p = 0
q = 0
a = 0
b = 0
sp = 0
sp_list = []
for row_loop in range(row_num):  # 0代表无法入逻辑，1代表完全匹配，2代表包含关系，3代表“第x”逻辑，4代表坐标判断
    t_1 = df.loc[row_loop, 'Hos_Source']
    t_2 = df.loc[row_loop, 'Hos_Preference']
    tem = fun_Simple_Processor(t_1, t_2)  # 主方法1，简单逻辑处理字符串
    if tem == 0:
        tem = fun_Coordinate_Processor(t_1, t_2)
    df.iloc[row_loop, column_num - 2] = tem  # 写入是瓶颈，要注意尽量减少写入次数

    # ************************统计模块*****************
    #     if df.iloc[row_loop,5] == 1:
    #         i = i+1
    #     if df.iloc[row_loop, 5] == 2:
    #         j = j+1
    #     if df.iloc[row_loop,5] == 3:
    #         p = p+1
    #     if df.iloc[row_loop,5] == 4:
    #         a = a+1
    #     if df.iloc[row_loop,5] == -1:
    #         q = q+1
    #     if df.iloc[row_loop,5] == -2:
    #         b = b+1
    #     if df.iloc[row_loop,5] == 0:
    #         sp = sp + 1
    #         sp_list.append(row_loop)
    #
    # print('直接匹配：',i,i/row_num)
    # print('包含关系（不含第x逻辑）：',j,j/row_num)
    # print('第x逻辑：',p,p/row_num)
    # print('百度坐标（球面距离5km以内）：',a,a/row_num)
    # print('第x逻辑（必不成立）：',q,q/row_num)
    # print('百度坐标（球面距离5km以外）：',b,b/row_num)
    # print('特殊情况，未入逻辑：',sp,sp/row_num)
    # print(sp_list)
    # ************************统计模块*****************
    # ************************打个补丁*****************
    # distance = 0
    # if df.iloc[row_loop, 5] == 4:
    #     t_1 = df.loc[row_loop, 'Hos_Source']
    #     t_2 = df.loc[row_loop, 'Hos_Preference']
    #     distance = fun_Coordinate_Processor_another(t_1, t_2)
    #     df.iloc[row_loop, 6] = distance
    #
    distance = df.iloc[row_loop, 6]
    print('编号:'+str(row_loop))
    print('Hos_Source:'+df.iloc[row_loop, 3])
    print('Hos_Preference:' + df.iloc[row_loop, 4])
    print('distance: %f' %distance )

# ***************************所有操作写在上面****************************
print_time()
df.to_excel(t, sheet_name='Sheet1', index=False, header=True)
print_time()

# pip install C:\ProgramData\Anaconda3\Scripts\geopy-1.20.0-py2.py3-none-any.whl
