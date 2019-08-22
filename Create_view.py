# coding = utf-8
import cx_Oracle
from collections.abc import Iterable # 最新的写法
import time
import xlsxwriter

def print_time ():
    global time_1
    tem_t = time.time()
    tem = tem_t - time_1
    z = round(tem,3)
    print ("累计消耗时间为:"+str(z))

time_1 = time.time()

def get_sql_list(user_name,password,dsn_tst,sql):
    print_time()

    connect = cx_Oracle.connect(user_name,password,dsn_tst)
    cursor = connect.cursor() # 链接

    print_time()

    cursor.execute(sql) # 执行
    list = cursor.fetchall()

    print_time()

    cursor.close()
    connect.close()
    return list

def Excl_wri(worksheet, line, list_1, str):
    worksheet.write(line, list_1, str)

user_name = '123'
password = '123123'
dsn_tst = cx_Oracle.makedsn('主机名', '端口', '服务名') # 基本信息
sql = "SELECT source.hcp_name as SOURCE_NAME,reference.province,reference.city,source.hco_name AS SOURCE_HOSPITAL," \
      "reference.name AS REFERENCE_HOSPITAL FROM source,reference " \
      "where reference.hcp_name = source.hcp_name and instr(source.province_name,reference.province)>0 and " \
      "instr(source.city_name,reference.city)>0 order by source.hcp_name"
sql = "select * from v4" # 具体视图名称
sql_list = get_sql_list(user_name,password,dsn_tst,sql)

# ***********************写入文件模块*******************************
workbook_goal = xlsxwriter.Workbook('root')
worksheet = workbook_goal.add_worksheet()
worksheet.set_column('A:A', 20)
worksheet.set_column('B:B', 20)
worksheet.set_column('C:C', 20)
worksheet.set_column('D:D', 40)
worksheet.set_column('E:E', 40)
worksheet.write(0, 0, 'Name')
worksheet.write(0, 1, 'Province_From_Preference')
worksheet.write(0, 2, 'City_From_Preference')
worksheet.write(0, 3, 'Hos_Source')
worksheet.write(0, 4, 'Hos_Preference') # 修改为具体的列名称
# ***********************以上为写入文件模块*************************

print_time()
i = 1
for loop_turple in sql_list:
    j = 0
    for loop in loop_turple:
        Excl_wri(worksheet,i,j,loop)
        j = j+1
    i = i+1

workbook_goal.close()
print_time()
print('Finish_Processing')

# ******************以上脚本完成视图生成并拷贝入excel*************************
# ******************以下为语句留档*****************

# print(cursor.fetchall()) # 为可循环量，获取一次后即为空
