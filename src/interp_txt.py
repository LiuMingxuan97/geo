import numpy as np
from scipy.interpolate import lagrange
from scipy.interpolate import CubicSpline

from scipy.spatial.transform import Slerp, Rotation as R



def lagrange_interp(time_list: list, value_list: list, timestamp: float):
    """插值操作
    Args:

        time_list (list): 时间-x
        value_list (list): 数值-y
    Return:
    ----
        polynomial : numpy.poly1d instance
    """
    cs = CubicSpline(time_list, value_list)
    # 计算插值后的 y 值
    y = cs(timestamp)
    return y


def slerp(q0:list, q1:list, delta_t):
    """
    使用四元数的球面线性插值 (SLERP) 方法
    Args:
        q0 (np.array): 起始四元数 (q0)
        q1 (np.array): 目标四元数 (q1)
        t (float): 插值参数，范围在 [0, 1] 之间，0 返回 q0，1 返回 q1
    Returns:
        np.array: 插值后的四元数
    """
    # 计算两个四元数的点积（内积）
    dot_product = np.dot(q0, q1)

    # 如果点积为负，则反转 q1 以确保最短路径
    if dot_product < 0.0:
        q1 = -q1
        dot_product = -dot_product

    # 避免浮点数精度问题导致 acos 越界
    dot_product = np.clip(dot_product, -1.0, 1.0)

    # 计算插值角度
    theta = np.arccos(dot_product)  # 角度
    sin_theta = np.sin(theta)

    # 处理非常接近的四元数，以避免分母为零的情况
    if sin_theta < 1e-6:
        return (1.0 - delta_t) * q0 + delta_t * q1

    # 计算插值四元数
    ratio_a = np.sin((1.0 - delta_t) * theta) / sin_theta
    ratio_b = np.sin(delta_t * theta) / sin_theta

    # 返回插值后的四元数
    return ratio_a * q0 + ratio_b * q1




def get_time_value(pos_file_path:str, qua_list_path:list, timestamp):
    """读取wgs84位置信息,四元数信息

    Args:
        file_path (str): 文件地址
    """
    time_value_list = []
    pos_x_list = []
    pos_y_list = []
    pos_z_list = []
    with open(pos_file_path, 'r') as pos_f:
        lines_info = pos_f.readlines()
        for line_info in lines_info:
            dat = line_info.strip().split('\t')
            time_value_list.append(float(dat[0]))
            pos_x_list.append(float(dat[1])/100)
            pos_y_list.append(float(dat[2])/100)
            pos_z_list.append(float(dat[3])/100)
    with open(qua_list_path, 'r') as qua_f:

        qua_lines_info = qua_f.readlines()
        for i in range(len(qua_lines_info)):
            dat = qua_lines_info[i].split('\t')
            if float(dat[0]) >= timestamp:
                dat = qua_lines_info[i-1].split('\t')
                t0 = float(dat[0])
                q0 = [dat[2], dat[3], dat[4], dat[1]] # [ dat[1], dat[2], dat[3], dat[4]]
                dat = qua_lines_info[i].split('\t')
                t1 = float(dat[0])
                q1 = [dat[2], dat[3], dat[4], dat[1]]  # [dat[2], dat[3], dat[4], dat[1]]
                break
        # print(q0)
        # print(q1)
        rotations = R.from_quat([q0,q1])

        # 使用 Slerp 进行插值
        slerp = Slerp([t0,t1], rotations)

        # 要计算的时间点
        # target_time = 781416468.5904029608

        # 计算插值结果
        interp_rotation = slerp(timestamp)
        interp_quat = interp_rotation.as_quat()
        # print(interp_quat)
            
            
            
            
            
    #     for line_info in qua_lines_info:
    #         dat = line_info.split(' ')
            
    #         if int(float(dat[0])) == int(timestamp):
    #             q0 = [dat[1], dat[2], dat[3], dat[4]]
    # print(q0)
    
    # 插值函数
    interp_x = lagrange_interp(time_value_list, pos_x_list, timestamp)
    interp_y = lagrange_interp(time_value_list, pos_y_list, timestamp)
    interp_z = lagrange_interp(time_value_list, pos_z_list, timestamp)
    
    
    return interp_x, interp_y, interp_z, interp_quat


if __name__=='__main__':
    qua_file = './data/test.att'
    pos_file_path = './data/test.eph'
    interp_x, interp_y, interp_z, interp_quat = get_time_value(pos_file_path, qua_file, 120542307.073383)
    print(interp_x, interp_y, interp_z, interp_quat)
