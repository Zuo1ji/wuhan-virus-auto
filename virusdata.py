import requests
import re
import json
import cv2
from pypinyin import lazy_pinyin
import pyecharts.options as opts
from pyecharts.charts import Map
from pyecharts.render import make_snapshot
from snapshot_phantomjs import snapshot
from pyecharts.globals import ThemeType

class virusstr:
    def __init__(self, targetProvinceName, additionProvinceName, gotProvinceName, additionMapName, mapname="map", virusname="virus"):
        self.targetProvinceName=targetProvinceName
        self.additionProvinceName=additionProvinceName
        self.gotProvinceName=gotProvinceName
        self.additionMapName=additionMapName
        self.mapname=mapname
        self.virusname=virusname
        self.chinaConfirmCount = 0
        self.s=''
        self.response = requests.get('https://3g.dxy.cn/newh5/view/pneumonia')
        self.response.encoding = 'utf-8'
        with open('cityname.json','r', encoding='UTF-8') as f1:
            self.cities=json.load(f1)
        with open('country.json','r', encoding='UTF-8') as f2:
            self.country=json.load(f2)
      
    def showProvinceInfo(self, province):
        provinceName = province.get('provinceShortName')
        provinceConfirmedCount = province.get('confirmedCount')
        provinceDeadCount = province.get('deadCount')
        provinceCuredCount = province.get('curedCount')

        displayString = "%s 确: %s   亡: %s   愈: %s\n" % (
            provinceName, provinceConfirmedCount, provinceDeadCount, provinceCuredCount)
        self.s=self.s+displayString

        if provinceName in self.gotProvinceName:
            cityList = province.get('cities')
            for city in cityList:
                cityDataStr = "%s 确:%s   亡:%s   愈:%s\n" % (city.get('cityName'), city.get(
                    'confirmedCount'), city.get('deadCount'), city.get('curedCount'))
                self.s=self.s+'--'+cityDataStr
        self.s=self.s

    def replacestr(self, s, keyvalue):
        s1=','.join(s)
        for key,value in keyvalue.items():
            s2=s1.replace(key,value)
            s1=s2
        return(s1.split(','))

    def getadditionMapName(self,province):
        provincename=province.get("provinceShortName")
        if provincename in self.additionMapName:
            data1=[x["cityName"] for x in province["cities"]]
            data2=[x["confirmedCount"] for x in province["cities"]]
            data=[list(z) for z in zip(self.replacestr(data1,self.cities[provincename]),data2)]
            c = (
                Map(init_opts=opts.InitOpts(width="600px", height="400px"))
                .add(provincename+"肺炎地图", data_pair=data, maptype=provincename, is_map_symbol_show=False)
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
            make_snapshot(snapshot,c.render(''.join(lazy_pinyin(provincename))+"virusmap.html"), "dst1.png")
            img=cv2.imread("dst1.png",cv2.IMREAD_UNCHANGED)
            cv2.imwrite(''.join(lazy_pinyin(provincename))+"virusmap.png", img, [int(cv2.IMWRITE_PNG_COMPRESSION), 9])
    
    def getWorldMap(self):
        rawresult = re.search('<script id="getListByCountryTypeService2">(.*)</script>', self.response.text)
        provincedata = re.search('\[.*\]', rawresult.group(1)).group(0).split('catch')
        finalresult = provincedata[0]
        finalresult = finalresult[0:-1]

        jsondata = json.loads(finalresult)
        data1=[x["provinceName"] for x in jsondata]
        data2=[x["confirmedCount"] for x in jsondata]
        data=[list(z) for z in zip(self.replacestr(data1,self.country),data2)]
        data.append(['China',self.chinaConfirmCount])

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
        make_snapshot(snapshot, c.render("world.html"), "dst2.png")
        img=cv2.imread("dst2.png",cv2.IMREAD_UNCHANGED)
        cv2.imwrite("world.png", img, [int(cv2.IMWRITE_PNG_COMPRESSION), 7])
        return "world.png"
        
    def getvirusstring(self):
        rawresult = re.search('<script id="getAreaStat">(.*)</script>', self.response.text)
        provincedata = re.search('\[.*\]', rawresult.group(1)).group(0).split('catch')

        finalresult = provincedata[0]
        finalresult = finalresult[0:-1]

        self.jsondata = json.loads(finalresult)

        chinaCuredCount = 0
        chinaDeadCount = 0

        for province in self.jsondata:
            self.chinaConfirmCount += province.get('confirmedCount')
            chinaDeadCount += province.get('deadCount')
            chinaCuredCount += province.get('curedCount')

        displayString = "全国 确: %s   亡: %s   愈 %s\n" % (
            self.chinaConfirmCount, chinaDeadCount, chinaCuredCount)
        self.s=self.s+displayString+'---\n'

        if self.targetProvinceName is 0:
            for province in self.jsondata:
                self.showProvinceInfo(province)
        else:
            for index in range(self.targetProvinceName):
                province = self.jsondata[index]
                self.showProvinceInfo(province)
        
        if len(self.additionMapName) > 0:
            for province in self.jsondata:
                self.getadditionMapName(province)

        for province in self.jsondata:
            provinceName = province.get('provinceShortName')
            if (provinceName in self.additionProvinceName) and (self.targetProvinceName != 0):
                self.showProvinceInfo(province)
        return self.s

    def getvirusimg(self):
        try:
            self.makevirusmap(self.jsondata)
        except:
            self.getvirusstring
            self.makevirusmap(self.jsondata)
        rawresult = re.search('<script id="getStatisticsService">(.*"abroadRemark":""\}\}catch\(e\)\{\})</script>', self.response.text)
        StatisticsService = re.search('window.getStatisticsService = (.*)}catch', rawresult.group(1))
        jsondata1 = json.loads(StatisticsService.group(1))
        virusimg=requests.get(jsondata1.get("dailyPic"))
        img = virusimg.content
        with open(self.virusname+".png","wb") as f:
            f.write(img)
        return self.virusname+".png", self.mapname+".png"

    def makevirusmap(self,jsondata1):
        data =[
            [[x["provinceShortName"], x["confirmedCount"]] for x in jsondata1]
        ][0]
        c = (
            Map(init_opts=opts.InitOpts(width="600px", height="400px",theme=ThemeType.ROMA))
            .add("商家A", data_pair=data, maptype="china", is_map_symbol_show=False)
            .set_global_opts(
                visualmap_opts=opts.VisualMapOpts(
                    is_piecewise=True,
                    pieces=[
                        {"min": 1001, "label": ">1000", "color": "#731919"},
                        {"min": 500, "max": 1000, "label": "500 - 1000", "color": "#9c2f31"},
                        {"min": 100, "max": 499, "label": "100 - 499", "color": "#c34548"},
                        {"min": 10, "max": 99, "label": "10 - 99", "color": "#e26061"},
                        {"min": 1, "max": 9,  "label": "1 - 9", "color": "#f08f7f"},
                        {"max": 1, "label": "疑似", "color": "#f2d7a2"},
                    ]
                    ),
                legend_opts=opts.LegendOpts(is_show=False)
                )
        )
        make_snapshot(snapshot, c.render(self.mapname+".html"), "dst.png")
        img=cv2.imread("dst.png",cv2.IMREAD_UNCHANGED)
        cv2.imwrite(self.mapname+".png", img, [int(cv2.IMWRITE_PNG_COMPRESSION), 9])

if __name__ == "__main__":
    # 填写想看到的确诊人数前n的省份
    # 如果填0表示全部看
    targetProvinceName = 0

    # 除了前n的省份之外，还想额外看到的省份
    # 如果不填则不会展示
    additionProvinceName = {"四川"}

    # 想看的详细城市的省份
    # 如果不填则不会展示
    gotProvinceName = {"四川"}

    # 想看的详细地图的省份
    # 如果不填则不会展示
    additionMapName = {"四川"}

    v=virusstr(targetProvinceName, additionProvinceName, gotProvinceName, additionMapName)
    s=v.getvirusstring()
    str1,str2=v.getvirusimg()
    str3=v.getWorldMap()
    print(s)
