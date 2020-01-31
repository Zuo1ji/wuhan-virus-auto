from wxpy import *
import time
from virusdata import virusstr

# 填写想看到的确诊人数前n的省份
# 如果填0表示全部看
targetProvinceName = 0

# 除了前n的省份之外，还想额外看到的省份
# 如果不填则不会展示
additionProvinceName = {"四川"}

# 想看的详细城市的省份
# 如果不填则不会展示
gotProvinceName = {"湖北","四川"}

# 想看的详细地图的省份
# 如果不填则不会展示
additionMapName = {"四川"}

v=virusstr(targetProvinceName, additionProvinceName, gotProvinceName, additionMapName)
s=v.getvirusstring()
str1,str2=v.getvirusimg()

bot = Bot()

