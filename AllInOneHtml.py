import requests
import re
import json
import os
from PIL import Image
from io import BytesIO
import pyecharts.options as opts
from pyecharts.charts import Map
from pyecharts.globals import ThemeType
from pyecharts.commons.utils import JsCode
from pyecharts.components import Table
from pyecharts.components import Image as IMG
from pyecharts.options import ComponentTitleOpts

class pneumonia:
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
        rawresult = re.search('<script id="getAreaStat">(.*)</script>', self.response.text)
        provincedata = re.search('\[.*\]', rawresult.group(1)).group(0).split('catch')
        finalresult = provincedata[0]
        finalresult = finalresult[0:-1]
        self.jsondata = json.loads(finalresult)
      
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

    def getVirusString(self):
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

        for province in self.jsondata:
            provinceName = province.get('provinceShortName')
            if (provinceName in self.additionProvinceName) and (self.targetProvinceName != 0):
                self.showProvinceInfo(province)
        return self.s
    
    def MergeImage(self,urls,name,width=825, height=450):
        mergeimg = Image.new('RGB', (width, height*len(urls)), 255)
        x = 0
        y = 0
        for imgpath in urls:
            img=requests.get(imgpath["imgUrl"])
            image = Image.open(BytesIO(img.content))
            image = image.resize((width,height))
            mergeimg.paste(image,(x,y))
            y+=height
        mergeimg.save(name)
    
    def image_base(self,imgpath):
        image = IMG()
        img_src = (
                imgpath
        )
        image.add(
            src=img_src,
        ).set_global_opts()
        return image

    def getDailyImg(self):
        rawresult = re.search('<script id="getStatisticsService">(.*"治愈/死亡"\}\]\}\}catch\(e\)\{\})</script>', self.response.text)
        StatisticsService = re.search('window.getStatisticsService = (.*)}catch', rawresult.group(1))
        jsondata1 = json.loads(StatisticsService.group(1))

        quanguoTrendChart=jsondata1["quanguoTrendChart"]
        hbFeiHbTrendChart=jsondata1["hbFeiHbTrendChart"]
        self.MergeImage(quanguoTrendChart,"quanguoTrendChart.png")
        self.MergeImage(hbFeiHbTrendChart,"hbFeiHbTrendChart.png")

        return self.image_base("quanguoTrendChart.png"),self.image_base("hbFeiHbTrendChart.png")

    def getProvinceTable(self):
        jsondata1 = self.jsondata
        data =[
            [[x["provinceShortName"], x["currentConfirmedCount"], x["confirmedCount"], x["deadCount"], x["curedCount"]] for x in jsondata1]
        ][0]
        headers = ["地区", "现存确诊", "累计确诊", "死亡", "治愈"]
        table = Table()
        table.add(headers, data).set_global_opts()
        return table

    def getSichuanTable(self):
        jsondata1 = self.jsondata
        headers = ["地区", "现存确诊", "累计确诊", "死亡", "治愈"]
        for province in jsondata1:
            provincename=province.get("provinceShortName")
            if provincename in self.additionMapName:
                data =[
                    [[x["cityName"], x["currentConfirmedCount"], x["confirmedCount"], x["deadCount"], x["curedCount"]] for x in province["cities"]]
                ][0]
                table = Table()
                table.add(headers, data).set_global_opts()
                return table
    
    def getWorldTable(self):
        chinaConfirmCount = 0
        chinacurrentconfirmcount = 0
        chinaCuredCount = 0
        chinaDeadCount = 0

        for province in self.jsondata:
            chinacurrentconfirmcount += province.get('currentConfirmedCount')
            chinaConfirmCount += province.get('confirmedCount')
            chinaDeadCount += province.get('deadCount')
            chinaCuredCount += province.get('curedCount')
        chinadata=["亚洲","中国",chinacurrentconfirmcount,chinaConfirmCount,chinaDeadCount,chinaCuredCount]

        rawresult = re.search('<script id="getListByCountryTypeService2">(.*)</script>', self.response.text)
        provincedata = re.search('\[.*\]', rawresult.group(1)).group(0).split('catch')
        finalresult = provincedata[0]
        finalresult = finalresult[0:-1]
        jsondata = json.loads(finalresult)
        data =[
            [[x["continents"],x["provinceName"], x["currentConfirmedCount"], x["confirmedCount"], x["deadCount"], x["curedCount"]] for x in jsondata]
        ][0]
        data.extend([chinadata])
        TableData = sorted(data,key=lambda x: (x[0],-x[2]))
        headers = ["地区", "国家", "现存确诊", "累计确诊", "死亡", "治愈"]
        table = Table()
        table.add(headers, TableData).set_global_opts()
        return table

    def getSichuanMap(self,count,title):
        jsondata1 = self.jsondata
        for province in jsondata1:
            provincename=province.get("provinceShortName")
            if provincename in self.additionMapName:
                data1=[x["cityName"] for x in province["cities"]]
                data2=[x[count] for x in province["cities"]]
                data=[list(z) for z in zip(self.replacestr(data1,self.cities[provincename]),data2)]
                c = (
                    Map(init_opts=opts.InitOpts(width="1000px", height="628px"))
                    .add("", data_pair=data, maptype=provincename, is_map_symbol_show=False)
                    .set_global_opts(
                        title_opts=opts.TitleOpts(title=title,  pos_left="center"),
                        tooltip_opts=opts.TooltipOpts(is_show=True, formatter='{b}:{c}'),
                        visualmap_opts=opts.VisualMapOpts(
                            is_piecewise=True,
                            pieces=[
                                {"min": 50.5, "label": ">50", "color": "#c34548"},
                                {"min": 9.5, "max": 50.5, "label": "10 - 50", "color": "#e26061"},
                                {"min": 4.5, "max": 9.5, "label": "5 - 9", "color": "#f08f7f"},
                                {"min": 0.5, "max": 4.5, "label": "1 - 4", "color": "#f2d7a2"},
                                {"max": 0.5, "label": "0", "color": "#ffffff"},
                            ]
                            ),
                        legend_opts=opts.LegendOpts(is_show=False)
                        )
                )
                return c
    
    def getChinaMap(self,count,title):
        jsondata1 = self.jsondata
        data =[
            [[x["provinceShortName"], x[count]] for x in jsondata1]
        ][0]
        c = (
            Map(init_opts=opts.InitOpts(width="1000px", height="628px"))
            .add("", data_pair=data, maptype="china", is_map_symbol_show=False)
            .set_global_opts(
                title_opts=opts.TitleOpts(title=title,  pos_left="center"),
                tooltip_opts=opts.TooltipOpts(is_show=True, formatter='{b}:{c}'),
                visualmap_opts=opts.VisualMapOpts(
                    is_piecewise=True,
                    pieces=[
                        {"min": 1000.5, "label": ">10000", "color": "#731919"},
                        {"min": 1000.5, "max": 10000.5, "label": "1001 - 10000", "color": "#9c2f31"},
                        {"min": 500.5, "max": 1000.5, "label": "501 - 1000", "color": "#c34548"},
                        {"min": 100.5, "max": 500.5, "label": "101 - 500", "color": "#e26061"},
                        {"min": 10.5, "max": 100.5,  "label": "11 - 100", "color": "#f08f7f"},
                        {"min": 0.5, "max": 10.5, "label": "1 - 10", "color": "#f2d7a2"},
                        {"max": 0.5, "label": "0", "color": "#ffffff"},
                    ]
                    ),
                legend_opts=opts.LegendOpts(is_show=False)
                )
        )
        return c

    def getWorldMap(self,count,title):     
        chinaConfirmCount=0
        for province in self.jsondata:
            chinaConfirmCount += province.get('confirmedCount')

        rawresult = re.search('<script id="getListByCountryTypeService2">(.*)</script>', self.response.text)
        provincedata = re.search('\[.*\]', rawresult.group(1)).group(0).split('catch')
        finalresult = provincedata[0]
        finalresult = finalresult[0:-1]
        jsondata = json.loads(finalresult)
        data1=[x["provinceName"] for x in jsondata]
        data2=[x[count] for x in jsondata]
        data=[list(z) for z in zip(self.replacestr(data1,self.country),data2)]
        data.append(['China',chinaConfirmCount])

        c = (
            Map(init_opts=opts.InitOpts(width="1000px", height="628px"))
            .add("", data_pair=data, maptype="world", is_map_symbol_show=False)
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
                title_opts=opts.TitleOpts(title=title,  pos_left="center"),
                tooltip_opts=opts.TooltipOpts(is_show=True, formatter='{b}:{c}'),
                visualmap_opts=opts.VisualMapOpts(
                    is_piecewise=True,
                    pieces=[
                        {"min": 1000.5, "label": ">1000", "color": "#a03919"},
                        {"min": 500.5, "max": 1000.5, "label": "501 - 1000", "color": "#d14e26"},
                        {"min": 100.5, "max": 500.5, "label": "101 - 500", "color": "#fb6739"},
                        {"min": 50.5, "max": 100, "label": "51 - 100", "color": "#f88966"},
                        {"min": 10.5, "max": 50.5, "label": "11 - 50", "color": "#f5a991"},
                        {"min": 0.5, "max": 10.5, "label": "1 - 10", "color": "#fad5c9"},
                        {"max": 0.5, "label": "0", "color": "#ffffff"},
                    ]
                    ),
                legend_opts=opts.LegendOpts(is_show=False)
                )
        )
        return c

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

    v=pneumonia(targetProvinceName, additionProvinceName, gotProvinceName, additionMapName)
    s=v.getWorldTable()
    s.render()