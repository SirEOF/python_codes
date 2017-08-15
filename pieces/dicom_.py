# coding=utf-8
import warnings

from dicom import read_file
from dicom.dataset import Dataset, FileDataset

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', category=UserWarning)
    import dicom.filebase


def get_tag_value(ds, tag_a, tag_b, default=None):
    """
    获取dataset
    :param ds: Dataset 待获取对象dataset
    :param tag_a: int 第一级tag十六进制数
    :param tag_b: int 第二级tag十六进制数
    :param default: object 缺省返回
    :return: object
    """
    val = ds.get((tag_a, tag_b), default=default)
    if hasattr(val, 'value'):
        return val.value
    else:
        return val


def monkey_patch_dicom():
    """
    修正dicom中DicomFileLike对象不释放内存问题
    """
    if hasattr(dicom.filebase.DicomIO, '__del__'):
        del dicom.filebase.DicomIO.__del__


def dcm4array(ds, reverse=False):
    """
    dcm文件转为g
    :param ds: DataSet dicom对象
    :param reverse: bool 是否翻颜色
    :return : array 二维数组
    """
    import numpy as np
    center = ds.WindowCenter
    width = ds.WindowWidth
    low = center - width / 2
    pixel_data = ds.pixel_array
    shape = pixel_data.shape
    pixel_data = np.fromstring(pixel_data, dtype=np.uint16)
    pixel_data = pixel_data.reshape(shape)
    pixel_data = (pixel_data - low) / width * 256
    if reverse:
        pixel_data = 256 - pixel_data
    pixel_data[pixel_data < 0] = 0
    pixel_data[pixel_data > 256] = 256
    return pixel_data


def dcm_file4jepg_file(dicom_path, out_path, reverse=False):
    """
    dcm转化jepg
    :param dicom_path: str dicom路径
    :param out_path: str 输出jepg路径
    :param reverse: bool 是否翻颜色
    """
    ds = read_file(dicom_path, force=True)
    pixel_data = dcm4array(ds, reverse=reverse)
    from cv2.cv2 import imwrite
    imwrite(out_path, pixel_data)


def make_up_file_dataset(filename, ds, implement_instance_uid='1.2.826.0.1.3680043.9.6991'):
    """
    把裸Dataset对象ds装载为可以存储的FileDataSet对象.
    :param filename: str 文件名
    :param ds: Dataset dicom对象
    :param implement_instance_uid: str icoom 中的 file_meta部分的实例实现的前缀, 需自行申请的前缀, 随意写也不会影响使用
    :return: FileDataset 可保存的dataset对象
    """
    meta = Dataset()
    meta.MediaStorageSOPClassUID = ds.SOPClassUID
    meta.MediaStorageSOPInstanceUID = ds[0x0008, 0x0018].value
    meta.ImplementationClassUID = implement_instance_uid
    fds = FileDataset(filename, {}, file_meta=meta, preamble=b"\0" * 128)
    fds.update(ds)

    fds.is_little_endian = True
    fds.is_implicit_VR = True
    return fds
