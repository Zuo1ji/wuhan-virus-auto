import requests
import re
import json
import cv2
import pyecharts.options as opts
from pyecharts.charts import Map
from pyecharts.render import make_snapshot
from snapshot_phantomjs import snapshot
from pyecharts.globals import ThemeType

class virusstr:
    def __init__(self, targetProvinceName, additionProvinceName, gotProvinceName, mapname="map", virusname="virus"):
        self.targetProvinceName=targetProvinceName
        self.additionProvinceName=additionProvinceName
        self.gotProvinceName=gotProvinceName
        self.mapname=mapname
        self.virusname=virusname
        self.s=''
        self.response = requests.get('https://3g.dxy.cn/newh5/view/pneumonia')
        self.response.encoding = 'utf-8'
        
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
        self.s=self.s+'\n'

    def getvirusstring(self):
        rawresult = re.search('<script id="getAreaStat">(.*)</script>', self.response.text)
        provincedata = re.search('\[.*\]', rawresult.group(1)).group(0).split('catch')

        finalresult = provincedata[0]
        finalresult = finalresult[0:-1]

        jsondata = json.loads(finalresult)
        
        self.makevirusmap(jsondata)

        chinaConfirmCount = 0
        chinaCuredCount = 0
        chinaDeadCount = 0

        for province in jsondata:
            chinaConfirmCount += province.get('confirmedCount')
            chinaDeadCount += province.get('deadCount')
            chinaCuredCount += province.get('curedCount')

        displayString = "全国 确: %s   亡: %s   愈 %s\n" % (
            chinaConfirmCount, chinaDeadCount, chinaCuredCount)
        self.s=self.s+displayString+'---\n\n'

        if self.targetProvinceName is 0:
            for province in jsondata:
                self.showProvinceInfo(province)
        else:
            for index in range(self.targetProvinceName):
                province = jsondata[index]
                self.showProvinceInfo(province)

        for province in jsondata:
            provinceName = province.get('provinceShortName')
            if (provinceName in self.additionProvinceName) and (self.targetProvinceName != 0):
                self.showProvinceInfo(province)
        
        return self.s

    def getvirusimg(self):
        rawresult = re.search('<script id="getStatisticsService">(.*"abroadRemark":""\}\}catch\(e\)\{\})</script>', self.response.text)
        StatisticsService = re.search('window.getStatisticsService = (.*)}catch', rawresult.group(1))
        jsondata1 = json.loads(StatisticsService.group(1))
        virusimg=requests.get(jsondata1.get("dailyPic"))
        img = virusimg.content
        with open(self.virusname+".png","wb") as f:
            f.write(img)
        return self.virusname+".png", self.mapname+".png"

    def makevirusmap(self,jsondata):
        data =[
            [[x["provinceShortName"], x["confirmedCount"]] for x in jsondata]
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
    gotProvinceName = {"湖北","四川"}

    v=virusstr(targetProvinceName, additionProvinceName, gotProvinceName)
    s=v.getvirusstring()
    str1,str2=v.getvirusimg()
