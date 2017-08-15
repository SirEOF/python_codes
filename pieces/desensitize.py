# coding=utf-8
import logging

import dicom.filebase
import numpy as np
from dicom import read_file
from dicom.tag import TupleTag

# 猴子补丁
if hasattr(dicom.filebase.DicomIO, '__del__'):
    del dicom.filebase.DicomIO.__del__

logger = logging.getLogger('desensitize')


def desensitize(ds, sensitive_tags=None, img_ds=True, img_ds_area=(None, None, None, None)):
    """ 脱敏函数
    :param ds: Dataset 待脱敏Dataset对象
    :param sensitive_tags: list 敏感标签
    :param img_ds: bool 是否进行图像脱敏
    :param img_ds_area: tuple 图像脱敏区域(x_min, x_max, y_min, y_max) None 表示不限
    :return: Dataset 已脱敏对象
    """
    if not sensitive_tags:
        sensitive_tags = [
            (0x0008, 0x0080),
            (0x0008, 0x0081),
            (0x0008, 0x1040),
            (0x0010, 0x0010),
            (0x0033, 0x1013),
            (0x0019, 0x161b),
        ]
    # 标签脱敏
    for tag in sensitive_tags:
        tag = TupleTag(tag)
        logger.debug('Desensitizing %s tag.' % tag)
        ds.pop(tag, None)
    # 图像脱敏
    if ds[0x0008, 0x0060].value in ('CR', 'DR') and img_ds:
        logger.debug('Desensitizing pixels data')
        pixels = np.fromstring(ds.PixelData, dtype=np.uint16)
        pixels = pixels.reshape([ds.Rows, ds.Columns])
        pixels = fill_zero_color(pixels, img_ds_area)
        ds.PixelData = pixels.tostring()
    return ds


def fill_zero_color(pixels, img_ds_area=(None, None, None, None)):
    """ 把高亮填充为背景色
    :param pixels: str 图片像素序列 
    :param img_ds_area: tuple 图像脱敏区域(x_min, x_max, y_min, y_max) None 表示不限
    :return: str 处理好的像素序列
    """
    max_x, max_y = pixels.shape[0] - 1, pixels.shape[1] - 1
    up_limit, down_limit, left_limit, right_limit = (
        img_ds_area[0] or 0, img_ds_area[1] or max_x, img_ds_area[2] or 0, img_ds_area[3] or max_y
    )
    zero_indices = np.argwhere(pixels[up_limit: down_limit, left_limit: right_limit] == 0).tolist()
    # x表示行数, y表示列数
    left_group = []
    right_group = []
    for x, y in zero_indices:
        if y + left_limit < (max_y + 1) / 2:
            left_group.append((x, y))
        else:
            right_group.append((x, y))
    for group in (left_group, right_group):
        xs = [_[0] for _ in group] or [0]
        ys = [_[1] for _ in group] or [0]
        gx_min, gx_max, gy_min, gy_max = min(xs), max(xs), min(ys), max(ys)
        # avg = np.mean(pixels[gx_min: gx_max + 1, gy_min: gy_max + 1])
        pixels[
        gx_min + up_limit: gx_max + 1 + up_limit,
        gy_min + left_limit: gy_max + 1 + left_limit
        ] = np.ones((gx_max - gx_min + 1, gy_max - gy_min + 1)) * 65535
    return pixels


def desensitize_file(path, out_path=None, **kws):
    """ 对文件进行脱敏
    :param path: str 文件路径 
    :param out_path: str 输出路径
    """
    ds = read_file(path, force=True)
    ds = desensitize(ds, **kws)
    if not out_path:
        out_path = path
    ds.save_as(out_path)
