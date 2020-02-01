
import requests
import re
import json
import pyecharts.options as opts
from pyecharts.charts import Map
from pyecharts.globals import ThemeType

def getChinadata(res):
    rawresult = re.search('<script id="getAreaStat">(.*)</script>', res)
    provincedata = re.search('\[.*\]', rawresult.group(1)).group(0).split('catch')

    finalresult = provincedata[0]
    finalresult = finalresult[0:-1]

    js = json.loads(finalresult)
    chinaConfirmCount = 0
    for province in js:
        chinaConfirmCount += province.get('confirmedCount')
    
    return ['China',chinaConfirmCount]

with open('country.json','r', encoding='UTF-8') as f:
    country=json.load(f)

def replacestr(s):
    s1=','.join(s)
    for key,value in country.items():
        s2=s1.replace(key,value)
        s1=s2
    return(s1.split(','))

response = requests.get('https://3g.dxy.cn/newh5/view/pneumonia')
response.encoding = 'utf-8'

rawresult = re.search(
    '<script id="getListByCountryTypeService2">(.*)</script>', response.text)
provincedata = re.search(
    '\[.*\]', rawresult.group(1)).group(0).split('catch')

finalresult = provincedata[0]
finalresult = finalresult[0:-1]

jsondata = json.loads(finalresult)
data1=[x["provinceName"] for x in jsondata]
data2=[x["confirmedCount"] for x in jsondata]
data=[list(z) for z in zip(replacestr(data1),data2)]
data.append(getChinadata(response.text))

c = (
    Map(init_opts=opts.InitOpts(width="1600px", height="900px"))
    .add("商家A", data_pair=data, maptype="world", is_map_symbol_show=False)
    .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    .set_global_opts(
        visualmap_opts=opts.VisualMapOpts(
            is_piecewise=True,
            pieces=[
                {"min": 100, "label": ">10000", "color": "#731919"},
                {"min": 14.5, "max": 100, "label": ">=15", "color": "#9c2f31"},
                {"min": 9.5, "max": 14.5, "label": "10 - 14", "color": "#c34548"},
                {"min": 4.5, "max": 9.5, "label": "5 - 9", "color": "#e26061"},
                {"min": 0, "max": 4.5, "label": "1 - 4", "color": "#f08f7f"},
            ]
            ),
        legend_opts=opts.LegendOpts(is_show=False)
        )
)
c.render("world.html")
