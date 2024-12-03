import json
import numpy as np


with open("./config/cameraInfo.json", "r") as file:
            config:dict = json.load(file)
            # 将矩阵转换为 NumPy 格式
R_cam2body = np.array(config["cam2body"])
Px:float = config["Px"]
Py:float = config["Py"]
F:float = config["F"]
principal_point_x:float = config["principal_point_x"]
principal_point_y:float = config["principal_point_y"]
