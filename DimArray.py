class DimArray:
    '''
    Служит для операций трансформирования массива строк
    изначально типа массив-в-массиве : [[][][]]
    потенциально заменяется numpy
    '''

    def __init__(self, base_arr, str_get_method=lambda x : x):
        self.base = base_arr
        self.str_get_method = str_get_method
        self.result = base_arr
        self.total_len = None
        self.len_scatter = None
        self.represent_len = None
        self.max_chars_in_line = None
        self.max_element_per_line = None

    def normalise(self, col_amount=None):
        '''для конструкции массив-в-массиве : [[][][]]
        отсутствие col_amount требует предварительного
        вызова collect_indicators'''
        if col_amount is None:
            col_amount = self.max_element_per_line
        self.result = [
            # хотя else покрывает оба случая - уменьшается читаемость
            item if len(item) == col_amount else item + [''] * (col_amount - len(item))
            for item in self.result
        ]

    def transpose(self):
        '''переворачиваем массив-матрицу (нормированный) на 90 град'''
        col_am = len(self.result[0])
        tmp_arr = []
        for idx in range(col_am):
            column = []
            for item in self.result:
                column.append(item[idx])
            tmp_arr.append(column)
        self.result = tmp_arr

    def linelize(self):
        '''снижение размерности массива
        если массив одномерный сохраняет поведение
        '''
        tmp_arr = []
        for row in self.result:
            if not isinstance(row, list):
                tmp_arr += [row]
                continue
            for item in row:
                tmp_arr += [item]
        self.result = tmp_arr

    def collect_indicators(self):
        ''' для двухмерного массива = матрицы
        расчет: общей длинны символов,
        сбор: таблица соотв - длинна > кол.вхождений'''
        total_len = 0
        len_change = {}
        self.max_element_per_line = None
        max_element_per_line = 0
        for row in self.result:
            if isinstance(row, list):
                if len(row) > max_element_per_line:
                    max_element_per_line = len(row)
                for item in row:
                    item  = self.str_get_method(item)
                    len_item = len(item)
                    total_len += len_item

                    try:
                        len_change[len_item] += 1
                    except KeyError:
                        len_change[len_item] = 1
            else:
                item = self.str_get_method(row)
                len_item = len(item)
                total_len += len_item

                try:
                    len_change[len_item] += 1
                except KeyError:
                    len_change[len_item] = 1
        self.max_element_per_line = max_element_per_line
        self.total_len = total_len
        self.len_scatter = len_change

    def compute_repr_word_len(self):
        '''расчет показательной длинны слова из
        всего массива'''
        len_change = self.len_scatter
        max_ratio_len = 1
        max_len = 1
        max_ratio_len__amount = 1
        max_ratio_len__amount = 1
        for len_ in len_change.keys():
            if len_change[len_] > max_ratio_len__amount:
                max_ratio_len__amount = len_change[len_]
                max_ratio_len = len_
            if len_ > max_len:
                max_len = len_
        #av_len = sum(len_change.keys()) / sum(len_change.values())
        self.represent_len = max_ratio_len

    def compute_sizes_for_A4(self, down_pages=1, left_pages=1, f__auto_resize = True, elem_amount_border = 14600):
        '''расчет количества симоволов в строке для
        соответствия соотношения сторон матрицы
        на бумаге к А4'''
        if f__auto_resize and self.total_len > elem_amount_border and (down_pages != 1 or left_pages != 1):
            left_pages = round(self.total_len/elem_amount_border)

        A4_ratio = (29*left_pages) / (21*down_pages)
        #one_line_high_char = 1
        curr_ratio, delimeter = 2, 1
        item_per_line_len = 2
        for tmp_delimeter in range(1, 1000):
            tmp_ratio = self.total_len * item_per_line_len/ tmp_delimeter ** 2
            if tmp_ratio < A4_ratio:
                break
            delimeter = tmp_delimeter
            curr_ratio = tmp_ratio
        self.max_chars_in_line = delimeter
        self.max_lines_amount = int(self.total_len / delimeter)
        print(curr_ratio, delimeter, delimeter / self.represent_len, '— A4 ratio params')

    def resize_by_max_line_len(self):
        '''на вход идет прямой массив строк [str, str, str]'''
        resize_arr = []
        summ__line_len = 0
        tmp_arr = []
        for item in self.result:
            # по нормированной длинне.
            # так как таблица - поля могут быть широкими
            summ__line_len += self.represent_len  # len(item)
            if summ__line_len > self.max_chars_in_line:
                summ__line_len = 0
                resize_arr.append(tmp_arr)
                tmp_arr = []
            tmp_arr.append(item)
        self.result = resize_arr

    def resize_by_max_line_amount(self):
        resize_arr = [[] for i in range(self.max_lines_amount)]
        over_arr_iter = None
        over_elem_iter = iter(self.result)
        while True:
            if over_arr_iter is None:
                over_arr_iter = iter(resize_arr)

            try:
                curr_el = next(over_elem_iter)
            except StopIteration:
                break

            try:
                curr_arr = next(over_arr_iter)
            except StopIteration:
                over_arr_iter = None
                continue

            curr_arr.append(curr_el)

        self.result = resize_arr

    def dioganal_mirroring(self):
        nw_arr = []
        curr_len_nw_arr = 0
        for column in self.result:
            nw_arr_idx = 0
            for item in column:
                while True:
                    try:
                        nw_arr[nw_arr_idx].append(item)
                        nw_arr_idx += 1
                        break
                    except:
                        nw_arr.append([None for i in range(curr_len_nw_arr)])
            curr_len_nw_arr += 1
        self.result = nw_arr

    def resize_2d_array_by_A4_dim_ratio(self, down_pages=1, left_pages=1):
        self.collect_indicators()
        self.linelize()
        self.compute_repr_word_len()
        self.compute_sizes_for_A4(down_pages, left_pages)
        self.resize_by_max_line_len()
        self.collect_indicators()
        self.normalise(self.max_element_per_line)
        self.dioganal_mirroring()

    @staticmethod
    def get_dimmed_ratio( list__2d, str_el_access = lambda x:x , **kwargs):
        dm = DimArray(list__2d, str_el_access)
        dm.collect_indicators()
        dm.linelize()
        dm.compute_repr_word_len()
        dm.compute_sizes_for_A4(**kwargs)
        dm.resize_by_max_line_amount()
        return dm.result
