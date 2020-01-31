import requests
import re
import json
import pyecharts.options as opts
from pyecharts.charts import Map
from pyecharts.globals import ThemeType

additionMapName = {"四川"}
city={
    '成都':'成都市',
    '绵阳':'绵阳市',
    '广安':'广安市',
    '南充':'南充市',
    '自贡':'自贡市',
    '达州':'达州市',
    '泸州':'泸州市',
    '甘孜州':'甘孜藏族自治州',
    '宜宾':'宜宾市',
    '遂宁':'遂宁市',
    '内江':'内江市',
    '巴中':'巴中市',
    '德阳':'德阳市',
    '广元':'广元市',
    '雅安':'雅安市',
    '乐山':'乐山市',
    '眉山':'眉山市',
    '凉山':'凉山彝族自治州',
    '资阳':'资阳市',
    '攀枝花':'攀枝花市',
    '阿坝州':'阿坝藏族羌族自治州'}

def replacestr(s):
    s1=','.join(s)
    for key,value in city.items():
        s2=s1.replace(key,value)
        s1=s2
    return(s1.split(','))

response = requests.get('https://3g.dxy.cn/newh5/view/pneumonia')
response.encoding = 'utf-8'
rawresult = re.search('<script id="getAreaStat">(.*)</script>', response.text)
provincedata = re.search('\[.*\]', rawresult.group(1)).group(0).split('catch')

finalresult = provincedata[0]
finalresult = finalresult[0:-1]

jsondata = json.loads(finalresult)

for province in jsondata:
    if province.get("provinceShortName") in additionMapName:
        data1=[x["cityName"] for x in province["cities"]]
        data2=[x["confirmedCount"] for x in province["cities"]]
        data=[list(z) for z in zip(replacestr(data1),data2)]
        c = (
            Map(init_opts=opts.InitOpts(width="1000px", height="600px"))
            .add("商家A", data_pair=data, maptype="四川", is_map_symbol_show=False)
            .set_global_opts(
                visualmap_opts=opts.VisualMapOpts(
                    is_piecewise=True,
                    pieces=[
                        {"min": 50, "label": ">50", "color": "#731919"},
                        {"min": 10, "max": 50, "label": "10 - 50", "color": "#9c2f31"},
                        {"min": 5, "max": 9, "label": "5 - 9", "color": "#c34548"},
                        {"min": 0, "max": 4, "label": "1 - 4", "color": "#e26061"},
                    ]
                    ),
                legend_opts=opts.LegendOpts(is_show=False)
                )
        )
        c.render("sc.html")