import codecs
import Core
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt

# 提供爬虫登陆的账号和密码
api = SentinelAPI('KangYonghui', 'insarcasm')

# 使用http://geojson.io/ 查询地点对于的GeoJson文件

# 选择下载区域的范围多边形文件
# mine.CreateJson(110.313285, 39.130764, 'sda.json')

footprint = geojson_to_wkt(read_geojson('map.geojson'))

# 登陆服务器查询结果
products = api.query(footprint,
                     platformname='Sentinel-1',
                     sensoroperationalmode='IW',
                     producttype='SLC',
                     orbitdirection = 'DSCENDING')
Core.getDownUrl(products, 'FuShunD.csv')
Core.WriteShpFile('FuShunD.csv','E:\\GIS\\FuShunD.shp')
