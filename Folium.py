import pandas as pd
import time
import cpca
from cpca import drawer

def print_time():
    global time_1
    tem_t = time.time()
    tem = tem_t - time_1
    z = round(tem, 3)
    print("累计消耗时间为:" + str(z))


time_1 = time.time()

t = 'root'
df = pd.read_excel(t, sheet_name="Sheet1")
row_num, column_num = df.shape
print_time()

text=[]
for row_loop in range(row_num):
    t_1 = df.loc[row_loop, '信度分析']
    t_2 = df.loc[row_loop, 'Province_From_Preference']
    t_3 = df.loc[row_loop, 'City_From_Preference']
    if t_1 >0:
        tem_t = str(t_2) + str(t_3)
        text.append(tem_t)
print_time()

df_map = cpca.transform(text)
drawer.draw_locations(df_map, "df.html")
print_time()
# drawer.draw_locations(df, "df.html")
