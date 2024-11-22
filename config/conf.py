import json
import numpy as np


with open("./config/cameraInfo.json", "r") as file:
            config = json.load(file)
            # 将矩阵转换为 NumPy 格式
R_cam2body = np.array(config["cam2body"])
Px = config["Px"]
Py = config["Py"]
F = config["F"]
principal_point_x = config["principal_point_x"]
principal_point_y = config["principal_point_y"]
