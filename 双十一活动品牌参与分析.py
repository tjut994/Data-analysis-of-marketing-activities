
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import warnings 
warnings.filterwarnings('ignore')

from bokeh.plotting import figure,show,output_file
from bokeh.models import ColumnDataSource

'''
(1)导入数据
'''
import os
os.chdir('C:\\Users\\Administrator\\Desktop\\项目电商打折套路解析')
#工作路径

df=pd.read_excel('双十一淘宝美妆数据.xlsx',sheetname=0)
df.fillna(0,inplace=True)
df.index=df['update_time']
df['date']=df.index.day
#加载数据，提取销售日期
'''
2）双十一当天在售商品占比情况
'''
data1=df[['id','title','店名','date']] #筛选数据
d1=data1[['id','date']].groupby(by='id').agg(['min','max'])['date'] #统计不同数据销售开始和结束日期

id_11= data1[data1['date']==11]['id']#筛选双十一当天售卖商品id
d2=pd.DataFrame({'id':id_11,'双十一当天是否售卖':True})
#筛选双十一当天售卖商品id
id_data=pd.merge(d1,d2,left_index=True,right_on='id',how='left')
id_data.fillna(False,inplace=True)
#合并数据
m=len(d1)
m_11=len(id_11)
m_pre=m_11/m
print('双十一活动参与的商家数量是%i个,占比为%.2f%%' %(m_11,m_pre*100))
'''
3）商品销售情况分类
'''
id_data['type']='待分类'
id_data['type'][(id_data['min']<11)&(id_data['max']>11)]='A'
id_data['type'][(id_data['min']<11)&(id_data['max']==11)]='B'
id_data['type'][(id_data['min']==11)&(id_data['max']>11)]='C'
id_data['type'][(id_data['min']==11)&(id_data['max']==11)]='D'
id_data['type'][id_data['双十一当天是否售卖']==False]='F'
id_data['type'][id_data['max']<11]='E'
id_data['type'][id_data['min']>11]='G'

result1=id_data['type'].value_counts()
result1=result1.loc[['A','C','B','D','E','F','G']]

from bokeh.palettes import brewer
colori=brewer['YlGn'][7]
plt.axis('equal')
plt.pie(result1,labels=result1.index,autopct='%.2f%%',colors=colori,
        startangle=90,radius=1,counterclock=False)

'''
4)未参与双十一当天活动的商品，去向如何
'''
id_not11=id_data[id_data['双十一当天是否售卖']==False]
df_not11=id_not11[['id','type']]
data_not11=pd.merge(df_not11,df,on='id',how='left')

id_con1=id_data['id'][id_data['type']=='F'].values

data_con2=data_not11[['id','title','date']].groupby(by=['id','title']).count()
title_count=data_con2.reset_index()['id'].value_counts()
id_con2=title_count[title_count>1].index

data_con3=data_not11[data_not11['title'].str.contains('预售')]
id_con3=data_con3['id'].value_counts().index

print('未参与双十一当天活动的商品中，%i个为暂时下架的商品，%i为重新上架的商品,%i个为预售商品'
      % (len(id_con1),len(id_con2),len(id_con3)))
'''
5)真正参与双十一的商品
'''
data_11sale = id_11
id_11sale_final = np.hstack((data_11sale,id_con3))
result2_i = pd.DataFrame({'id':id_11sale_final})

# 得到真正参与双十一活动的商品id

x1 =  pd.DataFrame({'id':id_11})
x1_df = pd.merge(x1,df,on = 'id', how = 'left')    # 筛选出真正参与活动中 当天在售的商品id对应源数据 
brand_11sale = x1_df.groupby('店名')['id'].count()
# 得到不同品牌的当天参与活动商品的数量

x2 =  pd.DataFrame({'id':id_con3})
x2_df = pd.merge(x2,df,on = 'id', how = 'left')    # 筛选出真正参与活动中 当天在售的商品id对应源数据 
brand_ys = x2_df.groupby('店名')['id'].count()
# 得到不同品牌的预售商品的数量

result2_data = pd.DataFrame({'当天参与活动商品数量':brand_11sale,
                            '预售商品数量':brand_ys})
result2_data['总数'] = result2_data['当天参与活动商品数量'] + result2_data['预售商品数量']
result2_data.sort_values(by = '总数',inplace = True,ascending = False)
result2_data

'''
图表制作
'''
from bokeh.models import HoverTool
from bokeh.core.properties import value

lst_brand = result2_data.index.tolist()
lst_type = result2_data.columns.tolist()[:2]
colors = ["#718dbf" ,"#e84d60"]

result2_data.index.name = 'brand'
result2_data.columns = ['sale_on_11','presell','sum']

source = ColumnDataSource(data=result2_data)


hover = HoverTool(tooltips=[("品牌", "@brand"),
                            ("双十一当天参与活动的商品数量", "@sale_on_11"),
                            ("预售商品数量", "@presell"),
                            ("参与双十一活动商品总数", "@sum")
                           ])  
output_file('project_pic1.html')
p = figure(x_range=lst_brand, plot_width=900, plot_height=350,
          title="各个品牌参与双十一活动的商品数量分布",
          tools=[hover,'reset,xwheel_zoom,pan,crosshair'])

p.vbar(top='sum',       
             x='brand',     
             source=source,
             width=0.9, alpha = 0.8,         
             )
show(p)

data2 = df[['id','title','店名','date','price']]
data2['period'] = pd.cut(data2['date'],[4,10,11,14],labels = ['双十一前','双十一当天','双十一后'])

price = data2[['id','price','period']].groupby(['id','price']).min()
price.reset_index(inplace = True)
# 针对每个商品做price字段的value值统计，查看价格是否有波动

id_count = price['id'].value_counts()
id_type1 = id_count[id_count == 1].index
id_type2 = id_count[id_count != 1].index
# 筛选出“不打折”和“真打折”的商品id
n1 = len(id_type1)
n2 = len(id_type2)
print('真打折的商品数量约占比%.2f%%，不打折的商品数量约占比%.2f%%' % (n2/len(id_count)*100, n1/len(id_count)*100))
'''
打折商品折扣情况
'''
output_file('project_pic2.html')
result3_data1 = data2[['id','price','period','店名']].groupby(['id','period']).min()
result3_data1.reset_index(inplace = True)

result3_before11 = result3_data1[result3_data1['period'] == '双十一前']
result3_at11 = result3_data1[result3_data1['period'] == '双十一当天']
result3_data2 = pd.merge(result3_at11,result3_before11,on = 'id')
# 筛选出商品双十一当天及双十一之前的价格

result3_data2['zkl'] = result3_data2['price_x'] / result3_data2['price_y']
# 计算折扣率
bokeh_data = result3_data2[['id','zkl']].dropna()

bokeh_data['zkl_range'] = pd.cut(bokeh_data['zkl'],bins = np.linspace(0,1,21))

bokeh_data2 = bokeh_data.groupby('zkl_range').count().iloc[:-1] # 这里去掉折扣率在0.95-1之间的数据，该区间内数据zkl大部分为1，不打折
bokeh_data2['zkl_pre'] = bokeh_data2['zkl']/bokeh_data2['zkl'].sum()
# 将数据按照折扣率拆分为不同区间

source = ColumnDataSource(data=bokeh_data2)
lst_brand = bokeh_data2.index.tolist()
hover = HoverTool(tooltips=[("折扣率", "@zkl")])  

p = figure(x_range=lst_brand, plot_width=900, plot_height=350, title="商品折扣率统计",
          tools=[hover,'reset,xwheel_zoom,pan,crosshair'])
p.line(x='zkl_range',y='zkl_pre',source = source,     
       line_width=2, line_alpha = 0.8, line_color = 'black',line_dash = [10,4])   
# 绘制折线图
p.circle(x='zkl_range',y='zkl_pre',source = source, size = 8,color = 'red',alpha = 0.8)

show(p)

data_zk = result3_data2[result3_data2['zkl']<0.95]  # 删除未打折数据
result4_zkld = data_zk.groupby('店名_y')['zkl'].mean()
# 筛选出不同品牌的折扣率

n_dz = data_zk['店名_y'].value_counts()
n_zs = result3_data2['店名_y'].value_counts()
result4_dzspbl = pd.DataFrame({'打折商品数':n_dz,'商品总数':n_zs})
result4_dzspbl['参与打折商品比例'] = result4_dzspbl['打折商品数'] / result4_dzspbl['商品总数']
result4_dzspbl.dropna(inplace = True)
output_file('project_pic3.html')
# 计算出不同品牌参与打折商品比例

result4_sum = result2_data.copy()
# 筛选出品牌参加双11活动的商品总数

result4_data = pd.merge(pd.DataFrame(result4_zkld),result4_dzspbl,left_index = True, right_index = True, how = 'inner')
result4_data = pd.merge(result4_data,result4_sum,left_index = True, right_index = True, how = 'inner')
# 合并数据
result3_data2

from bokeh.models.annotations import Span            # 导入Span模块
from bokeh.models.annotations import Label           # 导入Label模块
from bokeh.models.annotations import BoxAnnotation 

bokeh_data = result4_data[['zkl','sum','参与打折商品比例']]
bokeh_data.columns = ['zkl','amount','pre']
bokeh_data['size'] = bokeh_data['amount'] * 0.03
source = ColumnDataSource(bokeh_data)
# 创建ColumnDataSource数据

x_mean = bokeh_data['pre'].mean()
y_mean = bokeh_data['zkl'].mean()

hover = HoverTool(tooltips=[("品牌", "@index"),
                            ("折扣率", "@zkl"),
                            ("商品总数", "@amount"),
                            ("参与打折商品比例", "@pre"),
                           ])  # 设置标签显示内容
p = figure(plot_width=600, plot_height=600,
                title="各个品牌打折套路解析" , 
                tools=[hover,'box_select,reset,wheel_zoom,pan,crosshair']) 
# 构建绘图空间

p.circle_x(x = 'pre',y = 'zkl',source = source,size = 'size',
           fill_color = 'red',line_color = 'black',fill_alpha = 0.6,line_dash = [8,3])
p.ygrid.grid_line_dash = [6, 4]
p.xgrid.grid_line_dash = [6, 4]
# 散点图

x = Span(location=x_mean, dimension='height', line_color='green',line_alpha = 0.7, line_width=1.5, line_dash = [6,4])
y = Span(location=y_mean, dimension='width', line_color='green',line_alpha = 0.7, line_width=1.5, line_dash = [6,4])
p.add_layout(x)
p.add_layout(y)
# 绘制辅助线

bg1 = BoxAnnotation(bottom=y_mean, right=x_mean,fill_alpha=0.1, fill_color='olive')
label1 = Label(x=0.1, y=0.55,text="少量大打折",text_font_size="10pt" )
p.add_layout(bg1)
p.add_layout(label1)
# 绘制第一象限

bg2 = BoxAnnotation(bottom=y_mean, left=x_mean,fill_alpha=0.1, fill_color='firebrick')
label2 = Label(x=0.7, y=0.55,text="大量大打折",text_font_size="10pt" )
p.add_layout(bg2)
p.add_layout(label2)
# 绘制第二象限

bg3 = BoxAnnotation(top=y_mean, right=x_mean,fill_alpha=0.1, fill_color='firebrick')
label3 = Label(x=0.1, y=0.80,text="少量少打折",text_font_size="10pt" )
p.add_layout(bg3)
p.add_layout(label3)
# 绘制第三象限

bg4 = BoxAnnotation(top=y_mean, left=x_mean,fill_alpha=0.1, fill_color='olive')
label4 = Label(x=0.7, y=0.80,text="少量大打折",text_font_size="10pt" )
p.add_layout(bg4)
p.add_layout(label4)
# 绘制第四象限

show(p)





