import numpy as np
from pathlib import Path
import sys
sys.path.append(Path(__file__).absolute().parent.parent.as_posix())
from src.interp_api import get_time_value
from src.get_height import get_elevation_from_dem
from src.image2ground_h_api import CalLatLon, get_timestamp


def world_to_pixel(initial_pixel, world_point, height, lat_lon_func, time_lines, 
                eph_lines_info, qua_lines_info, threshold=0.1, max_iterations=20):
    """
    将地理坐标转换为图像像素坐标。
    
    :param initial_pixel: 初始像素坐标 (u, v)，作为迭代的起点 (tuple or list of floats)
    :param world_point: 目标地理坐标 (lat, lon) (tuple or list of floats)
    :param height: 高程值 (float)
    :param lat_lon_func: 函数，输入像素坐标 (u, v) 和高程 height，返回对应地理坐标 (lat, lon)
    :param threshold: 像素坐标收敛阈值 (float)
    :param max_iterations: 最大迭代次数 (int)
    
    :return: 收敛后的像素坐标 (u, v) 或 None（如果未收敛）
    """
    u, v = initial_pixel
    target_lat, target_lon = world_point

    for iteration in range(max_iterations):
        # 计算当前像素 (u, v) 对应的地理坐标
        current_lat, current_lon = lat_lon_func(u, v, height, time_lines, 
                eph_lines_info, qua_lines_info)
        
        # 计算 (u+1, v) 和 (u, v+1) 对应的地理坐标（数值偏导）
        lat_du, lon_du = lat_lon_func(u + 1, v, height, time_lines, 
                eph_lines_info, qua_lines_info)
        lat_dv, lon_dv = lat_lon_func(u, v + 1, height, time_lines, 
                eph_lines_info, qua_lines_info)
        
        # 计算雅可比矩阵的偏导数
        dlat_du = lat_du - current_lat
        dlon_du = lon_du - current_lon
        dlat_dv = lat_dv - current_lat
        dlon_dv = lon_dv - current_lon

        # 计算雅可比矩阵的行列式
        determinant = dlat_dv * dlon_du - dlat_du * dlon_dv
        if np.abs(determinant) < 1e-12:  # 避免奇异矩阵
            print("Jacobian determinant is close to zero. Iteration failed.")
            return None

        # 计算地理坐标的误差
        delta_lat = target_lat - current_lat
        delta_lon = target_lon - current_lon

        # 计算像素校正值
        delta_u = int((-dlon_dv * delta_lat + dlat_dv * delta_lon) / determinant)
        delta_v = int(( dlon_du * delta_lat - dlat_du * delta_lon) / determinant)

        # 更新像素坐标
        u += delta_u
        v += delta_v

        # 判断是否收敛
        if np.abs(delta_u) < threshold and np.abs(delta_v) < threshold:
            print(f"Converged in {iteration + 1} iterations.")
            return u, v

    print("Failed to converge within the maximum number of iterations.")
    return None


def lat_lon_func(u:int, v:int, height:float, line_file, pos_file, qua_file)->tuple[float, float]:
    line_num = u
    # pos_file = './data/test.eph'
    # qua_file = './data/test.att'
    # line_file = './data/test.it'
    # dem_path = './data/ENVI_DEM.tif'
    timestamp = get_timestamp(line_num, line_file )
    # timestamp = 120162968.627485s
    x,y,z,q = get_time_value(pos_file, qua_file, timestamp)
    # print("x:",x,"\ty:",y,"\tz:",z,"\tq:",q)
    obs_list = [x,y,z]
    # timestamps = 781416469
    sample_num = v
    cal = CalLatLon(timestamp, obs_list, q, sample_num, height)
    resutl = cal.process()
    return resutl

if __name__=='__main__':

    # 测试
    initial_pixel = (60000, 4096)  # 初始像素点
    world_point = (35.70912132741606, 102.83441894481841)  # 目标地理坐标
    height = 2478  # 高程

    pixel_coordinates = world_to_pixel(initial_pixel, world_point, height, lat_lon_func)
    print("Pixel coordinates:", pixel_coordinates)
