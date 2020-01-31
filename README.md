# 武汉肺炎病患数据全国及省市地图

 武汉肺炎病患数据+地图+趋势图

 爬取[丁香园](https://3g.dxy.cn/newh5/view/pneumonia)的数据，并使用[pyecharts](https://github.com/pyecharts/pyecharts)作地图，再使用[wxpy](https://github.com/youfou/wxpy)发送到指定微信群
 ![Image](/images/map.png)

 ![Image](/images/virus.png)

 会根据参数选择不同，生成不同的省市地图：
 ![Image](/images/sichuanvirusmap.png)

 # 安装
 python 3.7+
 ```shell
# 直接用pip安装
$ pip install -r requirements.txt
```
其中pyecharts部分用到 [snapshot-phantomjs](http://pyecharts.org/#/zh-cn/render_images?id=snapshot-phantomjs)

# 使用
修改wechat.py中参数后直接使用命令行
```shell
$ python wechat.py
```

 # 待解决的问题

 * 部分省无法生城地图
 * 地图图例中[视觉映射配置项](http://pyecharts.org/#/zh-cn/global_options?id=visualmapopts%ef%bc%9a%e8%a7%86%e8%a7%89%e6%98%a0%e5%b0%84%e9%85%8d%e7%bd%ae%e9%a1%b9)每一段的范围及文字的修改工作
 * 世界地图国家名称显示问题
 * ……

 # （施工中）
 

 # 感谢
 项目从[武汉肺炎病患数据的 Bitbar 插件](https://github.com/Anthonyeef/wuhan-virus-bitbar-plugin)获得灵感
 
 另外由于[武汉肺炎疫情实时动态省市地图](https://github.com/wuhan2020/wuhan2020)写的太多了不是很想看
