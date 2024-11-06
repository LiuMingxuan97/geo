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
from interp_txt import get_time_value

spice.furnsh('./conf/naif0012.tls')
spice.furnsh('./conf/earth_latest_high_prec.bpc')

class CalLatLon:
    """
    计算
    """
    def __init__(self, timestamps:float, obs_pos: list, quaternion:list, sample_num:int):
        self.timestamps = timestamps
        self.obs_pos = obs_pos
        self.quaternion = quaternion
        self.Px = 3.5e-6
        self.Py = 3.5e-6
        self.F = 1942.555e-3
        self.major_radius=6378134
        self.minor_radius=6356752.3
        # 以中心点为原点的 y, x 偏移
        self.pix_cam_id = (0,sample_num)
        (self.principal_point_x, self.principal_point_y) = (1.64, 0)
        
        
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
        R_cam2body = np.array([[-0.321, -0.766, -0.557],
                            [-0.383, 0.643, -0.663],
                            [0.866, 0, -0.5]])
        return R_cam2body
    
    def q_rotation(self):
    # 创建旋转矩阵对象
        r = Rotation.from_quat(self.quaternion)
        R_body2eci_q = r.as_matrix()
        return R_body2eci_q
    
    def eci2ecr(self):
        R_eci2ecr = np.ndarray(shape=(3,3), dtype=float, order='F')
        # sate_time = arrow.get(satatime)
        start_time = datetime(2021,1,1,0,0,0, tzinfo=timezone.utc)
        end_time = start_time + timedelta(seconds=self.timestamps)
        sate_time = end_time
        # print(sate_time)
        date_str = sate_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        print("date_str", date_str)

        et = spice.str2et(date_str)
        mat = spice.pxform('J2000', 'ITRF93',  et)
        for i in range(3):
            for j in range(3):
                R_eci2ecr[i,j] = mat[i][j] # / pow(3,0.5)
        return R_eci2ecr
    
    def cal_pos(self, vi):
    
        obs_x, obs_y, obs_z = self.obs_pos[0], self.obs_pos[1], self.obs_pos[2]
        A = (self.major_radius+1500) ** 2
        B = (self.minor_radius +1500) ** 2
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
        R_cam2body = self.cam2body()
        
        R_img2ecr = R_eci2ecr.dot(R_body2eci_q.dot(R_img2cam))
        v_i = np.dot(R_img2ecr, pos_cam_mm)
        ground_point = self.cal_pos(v_i)
        lat, lon, alt = pymap3d.ecef2geodetic(ground_point[0], ground_point[1], ground_point[2])
        print('\n',lat,'\t', lon, '\t',alt)
        return [ lat, lon]
        
def get_timestamp(line_num, time_file):
    with open(time_file, "r") as file:
        line = file.readlines()[line_num]
        dat = line.strip().split('\t')
        timestamp = float(dat[1])
        return timestamp
            

        
        
if __name__ == '__main__':
    
    line_num = 44475
    sample_num = 1172
    
    pos_file = './data/dingbiao.eph'
    qua_file = './data/dingbiao.att'
    line_file = './data/dingbiao.it'
    timestamp = get_timestamp(line_num, line_file )
    # timestamp = 120162968.627485
    x,y,z,q = get_time_value(pos_file, qua_file, timestamp)
    # print("x:",x,"\ty:",y,"\tz:",z,"\tq:",q)
    obs_list = [x,y,z]
    # timestamps = 781416469

    cal = CalLatLon(timestamp, obs_list, q, sample_num)
    resutl = cal.process()
    