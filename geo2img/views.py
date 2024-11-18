from pydantic import BaseModel, HttpUrl
from typing import List, Tuple
from ninja import Router, NinjaAPI, Query, Path, Schema, File, Form
from ninja.files import UploadedFile
import json
import sys
from pathlib import Path
sys.path.append(Path(__file__).absolute().parent.parent.parent.as_posix())
from src.interp_api import get_time_value
from src.image2ground_api import CalLatLon, get_timestamp
from ninja.errors import ValidationError



router = Router()

# class InputModel(BaseModel):
#     imgPoints: List[List[int]] 


@router.post(path = "img2geo", tags = ["first"], summary="像元坐标To地理坐标", description = "将图像坐标转换为地理坐标\n经纬度")

def test_api(request,
    attPath: UploadedFile = File(...),    # 接收文件
    itPath: UploadedFile = File(...),     # 接收文件
    ephPath: UploadedFile = File(...),    # 接收文件
    imgPoints: str  = Form(...)            # 从表单接收其他字段 ):
):
    pos_file = ephPath
    qua_file = attPath
    line_file = itPath
    
    # time_lines = line_file.read().decode().splitlines()
    # print(time_lines)
    
    
    img_points_list = json.loads(imgPoints)
    results = []
    # 读取时间文件
    time_lines = line_file.read().decode().splitlines()
    eph_lines_info = pos_file.read().decode().splitlines()
    qua_lines_info = qua_file.read().decode().splitlines()
    
    for line_sample in img_points_list:
        dem_path = './data/ENVI_DEM.tif'
        timestamp = get_timestamp(line_sample[0], time_lines )

        x,y,z,q = get_time_value(eph_lines_info, qua_lines_info, timestamp)
        obs_list = [x,y,z]

        cal = CalLatLon(timestamp, obs_list, q, line_sample[1], dem_path)
        resutl = cal.process()
        results.append(resutl)
    return {"status": "success", "message": "Data processed", "data": results}


    