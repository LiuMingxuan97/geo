from osgeo import gdal, ogr, osr

def get_elevation_from_dem(dem_path, longitude, latitude):
    # 打开DEM文件
    dem_dataset = gdal.Open(dem_path)
    if dem_dataset is None:
        print("无法打开DEM文件")
        return None

    # 获取DEM的地理参考信息
    dem_geotransform = dem_dataset.GetGeoTransform()
    dem_srs = dem_dataset.GetProjection()

    # 创建经纬度坐标点的OGR对象
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(longitude, latitude)

    # 将经纬度坐标点转换为DEM的投影坐标
    src_srs = osr.SpatialReference()
    src_srs.ImportFromEPSG(4326)  # WGS84坐标系统
    dst_srs = osr.SpatialReference()
    dst_srs.ImportFromWkt(dem_srs)
    transform = osr.CoordinateTransformation(src_srs, dst_srs)
    point.Transform(transform)

    # 将投影坐标转换为像素坐标
    x = int((point.GetX() - dem_geotransform[0]) / dem_geotransform[1])
    y = int((point.GetY() - dem_geotransform[3]) / dem_geotransform[5])

    # 读取像素值（即高程值）
    if x >= 0 and x < dem_dataset.RasterXSize and y >= 0 and y < dem_dataset.RasterYSize:
        elevation = dem_dataset.GetRasterBand(1).ReadAsArray(x, y, 1, 1)[0, 0]
        return elevation
    else:
        print("经纬度坐标点超出DEM范围")
        return None

# 示例用法
dem_path = "./data/ENVI_DEM.tif"  # 替换为你的DEM文件路径
longitude = 120.0  # 经度示例值
latitude = 30.0  # 纬度示例值
elevation = get_elevation_from_dem(dem_path, longitude, latitude)
if elevation is not None:
    print("高程值:", elevation)


