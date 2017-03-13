# coding=utf-8
from openpyxl.cell import Cell
from openpyxl.reader.excel import load_workbook

from django_tools.serializer import to_json


class TitledSheet(object):
    """ 名称解析excel
    """

    class _D:
        """ 穿透字典
        """
        def __getitem__(self, item):
            return int(item)

        def get(self, item, default=None):
            return item

    class _Indexed:
        """ 表索引类
        """

        DIRECTIONS = ['columns', 'rows']

        def __init__(self, sheet, column_map, row_map, resolve_cell=None):
            self.sheet = sheet
            self.columns_map = column_map
            self.rows_map = row_map
            self.resolve_cell = resolve_cell
            self.direction = self.DIRECTIONS[self.direction_index]
            self.matrix = self.make_matrix(self.sheet, self.direction)

        def __getitem__(self, item):
            map = getattr(self, self.direction + '_map')
            anti_map = getattr(self, self.DIRECTIONS[1 - self.direction_index] + '_map')
            if isinstance(item, (list, tuple)):
                assert len(item) == 2, 'index Error'
                coordinate = map.get(item[0], item[0]), anti_map.get(item[1], item[1])
                if self.direction == 'columns':
                    coordinate = coordinate[1], coordinate[0]
                rtn = self.sheet._cells[coordinate]
            else:
                l = self.matrix[map.get(item, item)]
                rtn = {}
                for k, v in anti_map.items():
                    rtn[k] = l[v - 1]
                    rtn[v - 1] = l[v - 1]
            if isinstance(rtn, Cell) and self.resolve_cell:
                return self.resolve_cell(rtn.value)
            return rtn

        @classmethod
        def make_matrix(cls, sheet, direction):
            rtn = list(getattr(sheet, direction))
            return rtn

    class _ColumnsIndexed(_Indexed):
        direction_index = 0

    class _RowsIndexed(_Indexed):
        direction_index = 1

    USE_FIRST = 'use_first'

    def __init__(self, worksheet, column_names=None, row_names=None, resolve_cell=None):
        self.worksheet = worksheet
        self.column_names = column_names
        if isinstance(column_names, (tuple, list)):
            assert isinstance(column_names, (list, tuple)), 'Param `column_names` must be a list or a tuple'
            self._column_map = {_[1]: _[0] + 1 for _ in enumerate(self.column_names)}
        elif column_names == self.USE_FIRST:
            first_row = self.worksheet.rows.next()
            self._column_map = {_.value: i + 1 for i, _ in enumerate(first_row)}
        else:
            self._column_map = self._D()
        self.row_names = row_names
        if isinstance(row_names, (tuple, list)):
            assert isinstance(row_names, (list, tuple)), 'Param `row_names` must be a list or a tuple'
            self._row_map = {_[1]: _[0] + 1 for _ in enumerate(self.row_names)}
        elif row_names == self.USE_FIRST:
            first_col = self.worksheet.columns.next()
            self._row_map = {_.value: i + 1 for i, _ in enumerate(first_col)}
        else:
            self._row_map = self._D()
        self.columns = self._ColumnsIndexed(self.worksheet, self._column_map, self._row_map, resolve_cell=resolve_cell)
        self.rows = self._RowsIndexed(self.worksheet, self._column_map, self._row_map, resolve_cell=resolve_cell)

    @classmethod
    def load_from_excel(cls, filename, sheet_name, column_names=None, row_names=None, resolve_cell=None):
        """ 加载excel
        :param filename: excel文件名
        :param sheet_name: sheet名
        :param column_names: 列名 None, TitledSheet.USE_FIRST或手动指定列名数组
        :param row_names: 行名 None, TitledSheet.USE_FIRST或手动指定行名数组
        :param resolve_cell: 解析cell的函数, 默认不解析, 返回Cell对象
        :return: TitledSheet
        """
        wb = load_workbook(filename)
        ws = wb.get_sheet_by_name(sheet_name)
        return cls(ws, column_names, row_names, resolve_cell=resolve_cell)


if __name__ == '__main__':
    ts = TitledSheet.load_from_excel('b.xlsx', 'Sheet1',
                                     row_names=TitledSheet.USE_FIRST,
                                     column_names=TitledSheet.USE_FIRST,
                                     resolve_cell=lambda x: x.split('\n') if x else x)
    print ','.join(ts.columns[u'有效接收', u'朋友E车'])
    print ','.join(ts.columns[2, u'朋友E车'])
    print ','.join(ts.columns[u'有效接收', 10])
    print ','.join(ts.columns[2, 10])
    
    n = ts.columns[2] # 取第2列
    print n[1].value
    print n[u'99好车'].value
    print ts.rows[2] # 取第2行
    print ts.rows[10, 2]
    print ','.join(ts.rows[10, 2])
