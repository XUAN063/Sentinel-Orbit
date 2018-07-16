import json
import codecs
import os.path
from osgeo import gdal
from osgeo import ogr, osr


def getDownUrl(products, fileName):
    ''' 根据获取的区域内所有的图像信息提取下载链接
        将其以文本格式保存在filename文件中
        Args：
            products：查询到区域所有的图像的信息集合
            filename：保存下载链接的文件名

    '''
    # 统计下载的影像个数
    couts = len(products.items())

    f = codecs.open(fileName, 'a', 'utf8')
    for num in range(0, couts):
        tmpUrl = list(products.items())[num][1]

        filename = tmpUrl['filename']  # 图像的文件名
        OribtNum = tmpUrl['relativeorbitnumber']  # 图像的轨道号
        downUrl = tmpUrl['link']  # 图像的下载链接
        footprint = tmpUrl['footprint']  # 图像的四个角点的坐标
        OrbitDirection = tmpUrl['orbitdirection']

        print(downUrl)

        f.write(filename + ',' + OrbitDirection+','+downUrl + ',' +
                str(OribtNum)+',' + footprint + '\n')

    f.close()
    print('下载已完成')


def str2attributesVec(strLine: '输入的需要分解的字符串'):
    ''' 把输入的字符串分解成为参数列表
        Args:
            strLine:输入的需要分解的字符串
        return：
            返回参数列表
    '''
    tmpVec = str(strLine).split(',')  # 分解字符串
    attriVector = []
    attriVector.append(tmpVec[0])  # 文件名
    attriVector.append(tmpVec[1])  # 轨道方向
    attriVector.append(tmpVec[2])  # 下载链接
    attriVector.append(int(tmpVec[3]))  # 轨道号
    attriVector.append(float(tmpVec[5].split(' ')[1]))  # 左上角纬度
    attriVector.append(float(tmpVec[5].split(' ')[0]))  # 左上角经度
    attriVector.append(str(strLine)[str(strLine).find('POLYGON'):])  # 多边形参数

    return attriVector


def WriteShpFile(csvFile: '下载的影像列表', shpFileName: '需要输出的shp文件的绝对路径'):
    ''' 根据输入的影像列表csv文件建立覆盖范围的shp文件
        Args：
            csvFile：下载的影像列表csv文件
            shpFileName：shp文件的绝对路径
    '''

    # 设定文件名和属性名的编码
    # 以便可以正确显示中文路径和属性
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
    gdal.SetConfigOption("SHAPE_ENCODING", "")

    # 注册所有驱动
    ogr.RegisterAll()

    # 获取Shp文件的驱动
    oDrive = ogr.GetDriverByName("ESRI Shapefile")
    if oDrive == None:
        print("驱动不可用")

    # 创建shp文件
    oDS = oDrive.CreateDataSource(shpFileName)
    if oDS == None:
        print("文件创建失败")

    # 给shp文件创建一个多边形的图层
    oLayer = oDS.CreateLayer("Polygon", None, ogr.wkbPolygon, [])

    # 给图层创建属性表
    # 文件的ID号
    oLayer.CreateField(ogr.FieldDefn("ID", ogr.OFTInteger))

    # 文件名
    file_name = ogr.FieldDefn('FileName', ogr.OFTString)
    file_name.SetWidth(100)
    oLayer.CreateField(file_name)

    # Orbit Direction
    orbit_direction = ogr.FieldDefn('OrbitDir', ogr.OFTString)
    orbit_direction.SetWidth(20)
    oLayer.CreateField(orbit_direction)

    # 下载链接属性
    of_downLoadUrl = ogr.FieldDefn('Url', ogr.OFTString)
    of_downLoadUrl.SetWidth(200)
    oLayer.CreateField(of_downLoadUrl)

    # 轨道号
    oLayer.CreateField(ogr.FieldDefn('OrbitNum', ogr.OFTInteger))

    # 覆盖范围左上角的经纬度
    oLayer.CreateField(ogr.FieldDefn('Latitude', ogr.OFTReal))
    oLayer.CreateField(ogr.FieldDefn('Longitude', ogr.OFTReal))

    attributeName = ['FileName', 'OrbitDir',
                     'Url', 'OrbitNum', 'Latitude', 'Longitude']

    # 打开下载文件获取参数
    csvFileHandle = open(csvFile)
    AllLines = csvFileHandle.readlines()
    csvFileHandle.close()

    # 文件的ID号
    File_ID = 1
    for tmpLine in AllLines:
        attVector = str2attributesVec(tmpLine)  # 获取参数列表
        oFeatureRectangle = ogr.Feature(oLayer.GetLayerDefn())  # 获取属性表
        oFeatureRectangle.SetField('ID', File_ID)  # 设置ID属性
        File_ID = File_ID+1
        for mm in range(0, 6):
            #oFeatureRectangle = ogr.Feature(oLayer.GetLayerDefn())
            # 设置其他属性
            # print(attributeName[mm])
            # print(attVector[mm])
            oFeatureRectangle.SetField(attributeName[mm], attVector[mm])

        #oFeatureRectangle = ogr.Feature(oLayer.GetLayerDefn())
        # 生成多边形矢量
        geomRectangle = ogr.CreateGeometryFromWkt(attVector[6].strip('\n'))
        oFeatureRectangle.SetGeometry(geomRectangle)
        oLayer.CreateFeature(oFeatureRectangle)

    # 设置投影参数
    source = osr.SpatialReference()
    source.ImportFromEPSG(4326)  # 4326：WGS84坐标系
    source.MorphToESRI()

    # 投影文件的绝对路径
    FileNameNoExtension = os.path.splitext(shpFileName)[0]
    prjFile = open(FileNameNoExtension+'.prj', 'w')

    if prjFile == None:
        print("创建投影文件失败")

    # 投影参数的写入和关闭
    prjFile.write(source.ExportToWkt())
    prjFile.close()

    print("数据集创建完成！\n")
    oDS = None


def dms2deg(dms):
    '''将dd.ffxxxx表示的角度换算成以度为单位的角度'''
    d = int(dms)
    m = int((dms - d) * 100)
    s = ((dms - d) * 100 - m) * 100
    deg = d + m / 60.0 + s / 3600.0
    return deg


def CreateJson(Lon, Lat, pathStr):
    ''' 以输入的经纬度为中心向外扩充成正方形
        扩展后的边长为0.0002度
        Args:
            Lon:输入的中心经度
            Lat:输入的中心纬度
            pathStr:输出的geoJson文件名
    '''

    with open('tmp.json') as json_file:
        data = json.load(json_file)
        json_file.close()
        corList = data['features'][0]['geometry']['coordinates'][0]

        # 左上角坐标
        corList[0][0] = dms2deg(Lon) - 0.0001  # 左上角经度
        corList[0][1] = dms2deg(Lat) - 0.0001  # 左上角纬度

        # 右上角坐标
        corList[1][0] = dms2deg(Lon) + 0.0001
        corList[1][1] = dms2deg(Lat) - 0.0001

        # 左下角坐标
        corList[2][0] = dms2deg(Lon) + 0.0001
        corList[2][1] = dms2deg(Lat) + 0.0001

        # 右下角坐标
        corList[3][0] = dms2deg(Lon) - 0.0001
        corList[3][1] = dms2deg(Lat) + 0.0001

        corList[4][0] = corList[0][0]
        corList[4][1] = corList[0][1]

        # 按照文件名写入Json文件
        f = open(pathStr, 'w')
        f.write(json.dumps(data, indent=2))
        f.close()
