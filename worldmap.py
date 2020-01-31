'''
ak = 'zDZ30GcVMna3TzSbH5h6T73H1STwA295'
        geo_cities_coords={}
        for x in province["cities"]:
            address = x["cityName"]
            get='http://api.map.baidu.com/geocoding/v3/?address='+address+'&output=json&ak='+ak
            res = requests.get(get)
            jsonaddress=json.loads(res.text)
            dic1={address:[jsonaddress["result"]["location"]['lng'],jsonaddress["result"]["location"]['lat']]}
            geo_cities_coords.update(dic1)
        with open('geo_cities_coords.json', 'w') as f:
            f.write(json.dumps(geo_cities_coords))
'''
import requests
import re
import json
import pyecharts.options as opts
from pyecharts.charts import Map
from pyecharts.globals import ThemeType

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

c = (
    Map(init_opts=opts.InitOpts(width="1600px", height="900px"))
    .add("商家A", data_pair=data, maptype="world", is_map_symbol_show=False)
    .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    .set_global_opts(
        visualmap_opts=opts.VisualMapOpts(
            is_piecewise=True,
            pieces=[
                {"min": 15.5, "label": ">=15", "color": "#731919"},
                {"min": 9.5, "max": 14.5, "label": "10 - 14", "color": "#9c2f31"},
                {"min": 4.5, "max": 9.5, "label": "5 - 9", "color": "#c34548"},
                {"min": 0, "max": 4.5, "label": "1 - 4", "color": "#e26061"},
            ]
            ),
        legend_opts=opts.LegendOpts(is_show=False)
        )
)
c.render("world.html")
