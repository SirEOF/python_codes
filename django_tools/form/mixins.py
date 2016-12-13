# coding=utf-8

class CleanFromRequiredFieldMixin:
    """ 用于弥补django的缺陷, 清理form时, 即: 就算已经抛出ValidationError依然会进入到clean方法.
    使用此Mixin的类必须继承自Form
    """

    class Missing:
        pass

    def get_required_fields(self):
        """ 作为form的函数, 获取当前form的必须字段
        :param self: 一个form
        :return: form的必须字段名列表
        """
        required_field_names = []
        for name, field in self.fields.iteritems():
            if field.required:
                required_field_names.append(name)
        return required_field_names

    def _check_required_fields(self):
        """ 检查必须字段是否存在, 如果全都存在则返回True, 否则为False
        """
        field_names = self.get_required_fields()
        data = self.cleaned_data
        values = filter(lambda n: data.get(n, self.Missing) is self.Missing, field_names)
        rtn = not bool(values)
        return rtn