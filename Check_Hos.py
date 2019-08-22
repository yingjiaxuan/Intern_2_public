import pandas as pd
import time

def print_time ():
    global time_1
    tem_t = time.time()
    tem = tem_t - time_1
    z = round(tem,3)
    print ("累计消耗时间为:"+str(z))

time_1 = time.time()

t = 'root'
t_2 = 'root_2'
df = pd.read_excel(t, sheet_name="Sheet1")

print_time()
row_num, column_num = df.shape
df['信度分析'] = None
for row_loop in range(row_num):
    df.iloc[row_loop,df.shape[1]-1] = 0
print_time()
df.to_excel(t_2, sheet_name='Sheet1', index=False, header=True)
print_time()
# *******************************此脚本生成初始表格*********************
