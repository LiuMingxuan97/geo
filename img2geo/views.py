from pydantic import BaseModel, HttpUrl
from typing import List, Tuple
from ninja import Router, NinjaAPI, Query, Path, Schema, File, Form
import logging
from ninja.files import UploadedFile
import json
import sys
from pathlib import Path

sys.path.append(Path(__file__).absolute().parent.parent.parent.as_posix())
from src.interp_api import get_time_value
from src.image2ground_h_api import CalLatLon, get_timestamp
from src.geo2img_api import world_to_pixel, lat_lon_func
from ninja.errors import ValidationError

logger = logging.getLogger(__name__)

router = Router()

class Geo2ImgRequest(BaseModel):
    attPath: HttpUrl
    itPath: HttpUrl
    ephPath: HttpUrl
    geoPoints: List[float]

@router.post(
    path="geo2img",
    tags=["second"],
    summary="地理坐标To像元坐标",
    description="将地理坐标 \n经纬度转换为图像坐标",
)
def geo2img(
    request,
    attPath: UploadedFile = File(...,description = '星敏信息文件'),  # 接收文件
    itPath: UploadedFile = File(..., description = '行时信息文件'),  # 接收文件
    ephPath: UploadedFile = File(..., description = 'GPS信息文件'),  # 接收文件
    geoPoints: str = Form(..., description = '[经度， 纬度， 高], float'),  # 从表单接收其他字段 ):
):
    pos_file = ephPath
    qua_file = attPath
    line_file = itPath
    geo_points_list = json.loads(geoPoints)

    results = []
    time_lines = line_file.read().decode().splitlines()
    eph_lines_info = pos_file.read().decode().splitlines()
    qua_lines_info = qua_file.read().decode().splitlines()
    initial_pixel = (60000, 4096)  # 初始像素点
    
    # 单点转换
    try:
        world_point = (geo_points_list[0], geo_points_list[1])
    except Exception as err:
        logger.info(err)

    height = geo_points_list[2]
    pixel_coordinates = world_to_pixel(
        initial_pixel,
        world_point,
        height,
        lat_lon_func,
        time_lines,
        eph_lines_info,
        qua_lines_info,
    )
    # 多点转换
    # for line_sample in geo_points_list:
    #     world_point = (line_sample[0], line_sample[1])
    #     height = line_sample[2]

    #     pixel_coordinates = world_to_pixel(
    #         initial_pixel,
    #         world_point,
    #         height,
    #         lat_lon_func,
    #         time_lines,
    #         eph_lines_info,
    #         qua_lines_info,
    #     )
    #     results.append(pixel_coordinates)
    
    return {
        "code": 0,
        "message": "Data processed",
        "data": [geo_points_list, pixel_coordinates],
    }
