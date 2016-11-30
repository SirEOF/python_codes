import re

from django.core.exceptions import ValidationError


def validate_id_number(id_number):
    """ 身份证号码校验
    :param str id_number: 待校验的身份证号码
    :return bool: 是否合法
    """
    weight = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    validate = '10X98765432'

    if not re.match(r'[\w]{17}[\dXx]', id_number):
        raise ValidationError(u'身份证号码格式错误', code='invalid')
    id_number = id_number.upper()
    last_char = id_number[-1]
    num_sum = sum([int(x) * weight[i] for i, x in enumerate(id_number[:17])])
    mode = num_sum % 11
    if not validate[mode] == last_char:
        raise ValidationError(u'身份证号码校验不通过', code='invalid')