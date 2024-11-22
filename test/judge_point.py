from shapely.geometry import Point, Polygon

# 定义四个经纬度点，构成多边形（按顺时针或逆时针顺序）
polygon_points = [
    (116.0, 39.0),  # 点 1
    (117.0, 39.0),  # 点 2
    (117.0, 40.0),  # 点 3
    (116.0, 40.0)   # 点 4
]

# 创建一个多边形
polygon = Polygon(polygon_points)

# 定义要判断的点
latitude, longitude = 116.5, 39.5
point = Point(latitude, longitude)

# 判断点是否在多边形内
is_inside = polygon.contains(point)
print("点在多边形内部" if is_inside else "点在多边形外部")
