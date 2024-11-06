import numpy as np
import pymap3d
import arrow
from datetime import datetime, timedelta, timezone
from scipy.spatial.transform import Rotation
from math import sin,cos
import spiceypy as spice
import math
from pathlib import Path
import sys
sys.path.append(Path(__file__).absolute().parent.as_posix())
from interp import get_time_value

spice.furnsh('./conf/naif0012.tls')
# spice.furnsh('PCK00010.TPC')
spice.furnsh('./conf/earth_latest_high_prec.bpc')

class CalLatLon:
    """
    计算
    """
    def __init__(self, timestamps:float, obs_pos: list, quaternion:list):
        self.timestamps = timestamps
        self.obs_pos = obs_pos
        self.quaternion = quaternion
        self.Px = 4.25e-6
        self.Py = 4.25e-6
        self.F = 2410.32e-3
        self.major_radius=6378134
        self.minor_radius=6356752.3
        # 以中心点为原点的 y, x 偏移
        self.pix_cam_id = (0.5,0.5)
        (self.principal_point_x, self.principal_point_y) = (-1232, 0)
        
        
    def pos_cam(self):
        pos_cam_mm = np.array([self.pix_cam_id[0] *self.Px , self.pix_cam_id[1]*self.Px, 1])
        # pos_cam_mm = np.array([self.pix_cam_id[0] , self.pix_cam_id[1], 1])
        # pos_cam_mm = np.array([0.0208 , (self.pix_cam_id[1]-17768/2)*self.Px, self.F])
        
        return pos_cam_mm
        
    def img2cam(self):
        fc = self.F
        x0 = self.principal_point_x * self.Px
        y0 = self.principal_point_y * self.Py
        R_img2cam = np.array([[0, -1, y0],
                            [1, 0, -x0],
                            [0, 0, -fc]])
        
        
        # R_img2cam = np.array([[self.principal_point_y,    0,                     0],
        #                     [0,                         self.principal_point_x,  0],
        #                     [-y0,                       -x0,                      fc]])
        # R_img2cam = np.array([
        #     [1, 0, 0],
        #     [0,  1,  0],
        #     [0,  0, 1]])
        
        return R_img2cam
    
    def cam2body(self):
        R_cam2body = np.array([[1, 0, 0],
                            [0, 1, 0],
                            [0, 0, 1]])
        return R_cam2body
    
    def q_rotation(self):
    # 创建旋转矩阵对象
        r = Rotation.from_quat(self.quaternion)
        R_body2eci_q = r.as_matrix()
        return R_body2eci_q
    
    def eci2ecr(self):
        R_eci2ecr = np.ndarray(shape=(3,3), dtype=float, order='F')
        # sate_time = arrow.get(satatime)
        start_time = datetime(2000,1,1,12,0,0, tzinfo=timezone.utc)
        end_time = start_time + timedelta(seconds=self.timestamps)
        sate_time = end_time
        # print(sate_time)
        date_str = sate_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        et = spice.str2et(date_str)
        mat = spice.pxform('J2000', 'ITRF93',  et)
        for i in range(3):
            for j in range(3):
                R_eci2ecr[i,j] = mat[i][j] # / pow(3,0.5)
        return R_eci2ecr
    
    def cal_pos(self, vi):
    
        obs_x, obs_y, obs_z = self.obs_pos[0], self.obs_pos[1], self.obs_pos[2]
        A = (self.major_radius+164.852865) ** 2
        B = (self.minor_radius +164.852865) ** 2
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
    
    def process(self):
        
        R_eci2ecr = self.eci2ecr()
        R_body2eci_q = self.q_rotation()
        R_img2cam = self.img2cam()
        pos_cam_mm = self.pos_cam()
        
        R_img2ecr = R_eci2ecr.dot(R_body2eci_q.dot(R_img2cam))
        v_i = np.dot(R_img2ecr, pos_cam_mm)
        ground_point = self.cal_pos(v_i)
        lat, lon, alt = pymap3d.ecef2geodetic(ground_point[0], ground_point[1], ground_point[2])
        print('\n',lat,',\t', lon)
        return [lat, lon]
        
        
        
if __name__ == '__main__':
    pos_file = './data/xsd10/XSD-10_PMS_230014018068_01_CCD-1.eph'
    qua_file = './data/xsd10/XSD-10_PMS_230014018068_01_CCD-1.att'
    timestamp = 781416468.7485100031
    x,y,z,q = get_time_value(pos_file, qua_file, timestamp)
    obs_list = [x,y,z]
    # timestamps = 781416469
    # obs_list = [367702.0700000000, -5086418.0400000000, 4533892.5000000000]
    # quaternion = [0.2486485904, 0.8776706662, -0.1656902200,   0.3747196682]
    cal = CalLatLon(timestamp, obs_list, q)
    resutl = cal.process()
    