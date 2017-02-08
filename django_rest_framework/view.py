# coding=utf-8
from django.http.response import JsonResponse


class SingleErrorResponse(JsonResponse):
    """ 单错误提示
    """

    def __init__(self, error_msg, status):
        if isinstance(error_msg, list):
            error_msg = error_msg[0]
        super(SingleErrorResponse, self).__init__({'detail': error_msg}, status=status)
