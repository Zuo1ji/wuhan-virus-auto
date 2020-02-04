from wxpy import *
import time
from virusdata import virusstr
from pypinyin import lazy_pinyin
import emoji

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

bot = Bot()
my21 = bot.groups().search('2013级21班')[0]

my21.send(s)
my21.send_image(str1)
my21.send_image(str3)
for i in str1:
    my21.send_image(i)
if len(additionMapName) > 0:
    for i in additionMapName:
        my21.send_image(''.join(lazy_pinyin(i))+"virusmap.png")
my21.send('----------')
my21.send(emoji.emojize('*来自:cloud:鱼昆的自动提醒*'))
