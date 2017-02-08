# coding=utf-8


dynamic_serializer_dict = {}


def DynamicSerializer(base_serializer):
    """ 获取指定基类的动态序列化器
    :param base_serializer: 基类序列化器
    :return: DynamicSerializer
    """

    global dynamic_serializer_dict

    base_serializer_name = base_serializer.__name__
    serializer_class = dynamic_serializer_dict.get(base_serializer_name)
    if serializer_class:
        return serializer_class

    class _DynamicSerializer(base_serializer):
        """
        基本的序列化类，提供可定制的字段
        """

        def __init__(self, *args, **kwargs):
            # Don't pass the 'fields' arg up to the superclass
            fields = kwargs.pop('fields', [])
            excludes = kwargs.pop('excludes', [])

            # Instantiate the superclass normally
            super(_DynamicSerializer, self).__init__(*args, **kwargs)

            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            forbidden = set(excludes)
            existing = set(self.fields.keys())
            for field_name in (existing - allowed) | forbidden:
                self.fields.pop(field_name)

        class Meta:
            fields = '__all__'

    return _DynamicSerializer
