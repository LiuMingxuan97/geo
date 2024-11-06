from pydantic import BaseModel, HttpUrl
from typing import List, Tuple
from ninja import Router, NinjaAPI, Query, Path, Schema
import sys
from pathlib import Path
sys.path.append(Path(__file__).absolute().parent.parent.parent.as_posix())
from src.interp_txt import get_time_value
from src.image2ground_txt import CalLatLon
from ninja.errors import ValidationError



router = Router()

class InputModel(BaseModel):
    attPath: str
    itPath: str
    ephPath: str
    imgPoints: List[Tuple[float,float]]

# 定义顶层模型
class RequestModel(BaseModel):
    input: InputModel



@router.post(path = "img2geo", tags = ["first"], summary="像元坐标To地理坐标", description = "将图像坐标转换为地理坐标\n经纬度")

def test_api(request, data:RequestModel ):
    pos_file = './data/test.eph'
    qua_file = './data/test.att'
    results = []

    for timestamp in data.input.imgPoints:
        print(timestamp)
        x,y,z,q = get_time_value(pos_file, qua_file, timestamp[0])
        # print("x:",x,"\ty:",y,"\tz:",z,"\tq:",q)
        obs_list = [x,y,z]
        # timestamps = 781416469
        # obs_list = [367702.0700000000, -5086418.0400000000, 4533892.5000000000]
        # quaternion = [0.2486485904, 0.8776706662, -0.1656902200,   0.3747196682]
        cal = CalLatLon(timestamp[0], obs_list, q)
        result = cal.process()
        results.append(result)
    return {"status": "success", "message": "Data processed", "data": results}


    