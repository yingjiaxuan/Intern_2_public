import pandas as pd
import time
import re
import json
import eventlet
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


# 匹配“第x”逻辑
def fun_Check_Num(t_1, t_2):
    n_1 = re.search(r'第[一二三四五六七八九]', t_1)
    n_2 = re.search(r'第[一二三四五六七八九]', t_2)
    if n_1 == None or n_2 == None:
        return 1234
    if n_1.group(0) == n_2.group(0):
        return True
    else:
        return False


# 调用api返回经纬度
def getlnglat(address):
    flag = 0
    eventlet.monkey_patch() # 必须加这一句
    with eventlet.Timeout(2, False):
        url = 'http://api.map.baidu.com/geocoding/v3/'
        output = 'json'
        ak = 'fP9kvD7LTE3qkoYmnVpPv7ScmmUUqnkr'  # 应用时改为企业ak，其余都不需要修改
        add = quote(address)  # 由于本文城市变量为中文，为防止乱码，先用quote进行编码
        uri = url + '?' + 'address=' + add + '&output=' + output + '&ak=' + ak
        req = urlopen(uri)
        res = req.read().decode()  # 将其他编码的字符串解码成unicode
        temp = json.loads(res)  # 对json数据进行解析
        # time.sleep(4) # 时停测试
        flag = 1
    if flag != 1:
        return 0,0
    if temp['status'] != 0:
        return temp['status'], None
    lng = temp['result']['location']['lng']
    lat = temp['result']['location']['lat']  # 纬度——latitude,经度——longitude
    return lat, lng


# 计算球面距离并同信度一并返回
def fun_Coordinate_Processor(t_1, t_2):
    tuple_1 = getlnglat(t_1)
    tuple_2 = getlnglat(t_2)
    if tuple_1[1] == None or tuple_2[1] == None:
        return 0,'Error'
    if tuple_1 == (0,0) or tuple_2 == (0,0):
        return 404,'404Error'
    distance = geodesic(tuple_1, tuple_2).km
    if distance > 5:
        return -2,distance
    else:
        return 4,distance



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

def fun_Main_Processor(t_1,t_2,Error_list):
    tem = fun_Simple_Processor(t_1, t_2)
    distance = 'Null'
    if tem == 0:
        tem, distance = fun_Coordinate_Processor(t_1, t_2)
    if tem == 404:
        Error_list.append(row_loop)
    return tem,distance,Error_list


if __name__ == '__main__':
    t = 'C:\Personal_File\DiskF\GSK_Intern_Oracle\Tem_file\SQL_FINAL_2.xlsx'
    df = pd.read_excel(t, sheet_name="Sheet1")
    row_num, column_num = df.shape
    print_time()

    Error_list = []
    for row_loop in range(10000):  # 0代表无法入逻辑，1代表完全匹配，2代表包含关系，3代表“第x”逻辑，4代表坐标判断
        t_1 = df.loc[row_loop, 'HCO_NAME_SOURCE']
        t_2 = df.loc[row_loop, 'HCO_NAME_TARGET']
        tem = fun_Simple_Processor(t_1, t_2)  # 主方法1，简单逻辑处理字符串
        distance = 'Null'
        if tem == 0:
            tem,distance = fun_Coordinate_Processor(t_1, t_2)
        df.iloc[row_loop, column_num - 2] = tem  # 写入是瓶颈，要注意尽量减少写入次数
        if tem == 404:
            Error_list.append(row_loop)

        # ************************打个补丁*****************
        if df.iloc[row_loop, column_num - 2] == 4 or df.iloc[row_loop, column_num - 2] == -2\
                or df.iloc[row_loop, column_num - 2] == 404: # 写入距离
            df.iloc[row_loop, column_num - 1] = distance

        print('编号:' + str(row_loop))  # 进度可视化
        print('HCO_NAME_SOURCE:' + df.loc[row_loop, 'HCO_NAME_SOURCE'])
        print('HCO_NAME_TARGET:' + df.loc[row_loop, 'HCO_NAME_TARGET'])
        print('Distance: %s' % distance)

    print (Error_list)

    for list_loop in Error_list: # 补上EOF
        t_1 = df.loc[list_loop, 'HCO_NAME_SOURCE']
        t_2 = df.loc[list_loop, 'HCO_NAME_TARGET']
        tem, distance = fun_Coordinate_Processor(t_1, t_2)
        df.iloc[list_loop, column_num - 2] = tem
        df.iloc[list_loop, column_num - 1] = distance


        # print('编号:' + str(row_loop)) #进度可视化
        # print('HCO_NAME_SOURCE:' + df.loc[row_loop, 'HCO_NAME_SOURCE'])
        # print('HCO_NAME_TARGET:' + df.loc[row_loop, 'HCO_NAME_TARGET'])
        # print('Distance: %s' % distance)

    # ***************************所有操作写在上面****************************
    print_time()
    t = 'C:\Personal_File\DiskF\GSK_Intern_Oracle\Tem_file\SQL_FINAL_3.xlsx'
    df.to_excel(t, sheet_name='Sheet1', index=False, header=True)
    print_time()

# pip install C:\ProgramData\Anaconda3\Scripts\geopy-1.20.0-py2.py3-none-any.whl
