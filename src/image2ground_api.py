import numpy as np
import pymap3d
import arrow
import json
from datetime import datetime, timedelta, timezone
from scipy.spatial.transform import Rotation
from math import sin,cos
import spiceypy as spice
import math
from pathlib import Path
from config.conf import R_cam2body, Px, Py, F, principal_point_x, principal_point_y
import sys
sys.path.append(Path(__file__).absolute().parent.as_posix())
from interp_api import get_time_value
from get_height import get_elevation_from_dem



spice.furnsh('./config/naif0012.tls')
spice.furnsh('./config/earth_latest_high_prec.bpc')

class CalLatLon:
    """
    计算
    """
    def __init__(self, timestamps:float, obs_pos: list, quaternion:list, sample_num:int, dem_path:str):
        self.timestamps = timestamps
        self.obs_pos = obs_pos
        self.quaternion = quaternion
        self.dem_path = dem_path
        self.Px = Px
        self.Py = Py
        self.F = F
        self.major_radius=6378134
        self.minor_radius=6356752.3
        # 以中心点为原点的 y, x 偏移
        self.pix_cam_id = (0,sample_num)
        self.principal_point_x, self.principal_point_y = (principal_point_x, principal_point_y)
        
        
    def pos_cam(self):
        pos_cam_mm = np.array([self.pix_cam_id[0] *self.Px , self.pix_cam_id[1]*self.Px, 1])
        return pos_cam_mm
        
    def img2cam(self):
        fc = self.F
        x0 = self.principal_point_x * self.Px
        y0 = self.principal_point_y * self.Py

        R_img2cam = np.array([[1, 0, -x0],
                            [0, 1, -y0],
                            [0, 0, fc]])
        
        return R_img2cam   
    
    def q_rotation(self):
    # 创建旋转矩阵对象
        r = Rotation.from_quat(self.quaternion)
        R_body2eci_q = r.as_matrix()
        return R_body2eci_q
    
    def eci2ecr(self):
        R_eci2ecr = np.ndarray(shape=(3,3), dtype=float, order='F')
        start_time = datetime(2021,1,1,0,0,0, tzinfo=timezone.utc)
        end_time = start_time + timedelta(seconds=self.timestamps)
        sate_time = end_time
        date_str = sate_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        et = spice.str2et(date_str)
        mat = spice.pxform('J2000', 'ITRF93',  et)
        for i in range(3):
            for j in range(3):
                R_eci2ecr[i,j] = mat[i][j] # / pow(3,0.5)
        return R_eci2ecr
    
    def cal_pos(self, vi, height):
    
        obs_x, obs_y, obs_z = self.obs_pos[0], self.obs_pos[1], self.obs_pos[2]
        A = (self.major_radius+height) ** 2
        B = (self.minor_radius +height) ** 2
        a = (vi[0]**2 + vi[1]**2) / A + vi[2] ** 2 / B
        b = 2*(( vi[0] * obs_x + vi[1] * obs_y) / A + vi[2] * obs_z / B)
        c = (obs_x ** 2 +obs_y ** 2) / A + obs_z ** 2 / B - 1
        
        d = b**2 - 4.0*a*c

        if d < 0 :
            result = - b / (2 * a)
        elif d == 0:
            result = - b / (2 * a)
        else:
            e = math.sqrt(d)
            x1 = (-b + e) / (2 * a)
            x2 = (-b - e) / (2 * a)
            if abs(x1) > abs(x2):
                result = x2
            else:
                result = x1
        ground_point = result * vi + self.obs_pos
        return ground_point
    
    def iterative_ground_point_calculation(self, v_i):
        previous_ground_point = None
        for _ in range(10):  # 最多迭代10次
            ground_point = self.cal_pos(v_i, 0 if previous_ground_point is None else int(elevation))
            lat, lon, alt = pymap3d.ecef2geodetic(ground_point[0], ground_point[1], ground_point[2])
            
            elevation = get_elevation_from_dem(self.dem_path, lon, lat)
            
            # 检查是否满足提前停止的条件
            if previous_ground_point is not None:
                dx = abs(ground_point[0] - previous_ground_point[0])
                dy = abs(ground_point[1] - previous_ground_point[1])
                if dx < 10 and dy < 10:
                    break  # 提前停止迭代
            
            previous_ground_point = ground_point  # 更新上一次的ground_point
        
        # 返回最后一次计算的lat, lon, alt
        return lat, lon, alt
    
    def process(self):
        
        R_eci2ecr = self.eci2ecr()
        R_body2eci_q = self.q_rotation()
        R_img2cam = self.img2cam()
        pos_cam_mm = self.pos_cam()
        # R_cam2body = self.cam2body()
        
        R_img2ecr = R_eci2ecr.dot(R_body2eci_q.dot(R_cam2body.dot(R_img2cam)))
        v_i = np.dot(R_img2ecr, pos_cam_mm)
        
        lat, lon, alt = self.iterative_ground_point_calculation(v_i)
        
        return [ lat, lon]

        
def get_timestamp(line_num, time_file):

    line = time_file[line_num]
    dat = line.strip().split('\t')
    timestamp = float(dat[1])
    return timestamp
            

        
        
if __name__ == '__main__':
    
    line_num = 101744
    
    # 11.08测试使用的行列号
    # cmos1
    # sample_num = -(8192-7089)
    # cmos2
    sample_num = 2462
    
    pos_file = './data/test.eph'
    qua_file = './data/test.att'
    line_file = './data/test.it'
    dem_path = './data/ENVI_DEM.tif'
    timestamp = get_timestamp(line_num, line_file )
    # timestamp = 120162968.627485s
    x,y,z,q = get_time_value(pos_file, qua_file, timestamp)
    # print("x:",x,"\ty:",y,"\tz:",z,"\tq:",q)
    obs_list = [x,y,z]
    # timestamps = 781416469

    cal = CalLatLon(timestamp, obs_list, q, sample_num, dem_path)
    resutl = cal.process()
    