import numpy as np
from pathlib import Path
import sys
sys.path.append(Path(__file__).absolute().parent.parent.as_posix())
from interp_api import get_time_value
from get_height import get_elevation_from_dem
from image2ground_txt import CalLatLon, get_timestamp


def world_to_pixel(initial_pixel, world_point, height, lat_lon_func, threshold=0.1, max_iterations=20):
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
        current_lat, current_lon = lat_lon_func(u, v, height)
        
        # 计算 (u+1, v) 和 (u, v+1) 对应的地理坐标（数值偏导）
        lat_du, lon_du = lat_lon_func(u + 1, v, height)
        lat_dv, lon_dv = lat_lon_func(u, v + 1, height)
        
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
        delta_u = (-dlon_dv * delta_lat + dlat_dv * delta_lon) / determinant
        delta_v = ( dlon_du * delta_lat - dlat_du * delta_lon) / determinant

        # 更新像素坐标
        u += delta_u
        v += delta_v

        # 判断是否收敛
        if np.abs(delta_u) < threshold and np.abs(delta_v) < threshold:
            print(f"Converged in {iteration + 1} iterations.")
            return u, v

    print("Failed to converge within the maximum number of iterations.")
    return None

# 示例：地理到像素映射的虚拟函数
def mock_lat_lon_func(u, v, height):
    """
    一个模拟的 (u, v) 到 (lat, lon) 的映射函数，用于测试。
    假设映射为线性变化，并引入简单的偏移和比例因子。
    """
    lat = 40.0 + 0.001 * u + 0.0005 * v
    lon = -100.0 + 0.0005 * u + 0.001 * v
    return lat, lon

# 测试
initial_pixel = (500, 500)  # 初始像素点
world_point = (49.5, -99.5)  # 目标地理坐标
height = 100  # 高程

pixel_coordinates = world_to_pixel(initial_pixel, world_point, height, mock_lat_lon_func)
print("Pixel coordinates:", pixel_coordinates)
