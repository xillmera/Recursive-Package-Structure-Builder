import datetime
import re
import pathlib
import pickle
from typing import Union
from DimArray import DimArray

# странный баг - не переключился интерпретатор с 3.9 на 3.10

class PrivateModuleError(BaseException) : pass
class BuiltinFoundExeption(BaseException) : pass

def time_mesurement (func):
    def proxy(*args, **kwargs):
        t1 = datetime.datetime.now()
        tmp = func(*args, **kwargs)
        t2 = datetime.datetime.now()
        res = t2-t1
        res = int(res.total_seconds())
        print(f'time_mesurement: выполнение {func.__name__} заняло {res} sec')
        return tmp
    return proxy

class SerializableSet(set):
    def __reduce__(self):
        return (self.__class__, (list(self),))


class SingleTonSet(SerializableSet):
    instance = None
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        if cls.instance is None:
            cls.instance = obj
        return cls.instance
    '''
    def __reduce__(self):
        # первая серилизуемая очищает осталье объекты
        self.instance = None
        return super().__reduce__()
    '''

class CLI_ChoseExceptionData:
    ''' command-line interface
    который позволяет выбрать какие данные убираются
    из словаря или списка (отдельные функции)
    '''

    class ElementList:
        class ElementNotFound(BaseException):
            pass
        class Element :
            def __init__(self, value, num, init_status = True, callback = None):
                self.value = value
                self.num = num
                self.is_chosen = init_status if not callback else False
                self.callback = callback

            def change_status(self):
                if self.callback:
                    self.callback()
                else:
                    self.is_chosen = False if self.is_chosen else True

            def set_status(self, status:bool):
                if not self.callback:
                    self.is_chosen = status

            def __str__(self):
                return f'[{"x" if self.is_chosen else " "}] {self.num}. {self.value}'


        def __init__(self, element_list: list):
            self.elements =[]

            num = 0
            for num, item in enumerate(element_list):
                self.elements.append(self.Element(item, num))
            self.elements.append(self.Element('<!> uncheck_all', num+1, callback=lambda : self.update_all()))
            self.elements.append(self.Element('<!>   check_all', num+2, callback=lambda : self.update_all(True)))

        def update_all(self, status = False):
            for item in self.elements:
                item.set_status(status)

        def change_status_for_num(self, num):
            for item in self.elements:
                if item.num == num :
                    item.change_status()
                    return
            raise self.ElementNotFound

        def chosen_ones (self):
            return [elem.value for elem in self.elements if elem.is_chosen ]

        def __str__(self):
            return '\n'.join(map(str,self.elements))

    INIT_MESSAGE = '''Режим изменения данных. 
    данные помеченые "x" окажутся в выходном массиве
    чтобы изменить состояние элемента - введите его номер
    чтобы завершить изменения введите любой символ кроме цифр
    '''

    SEPARATOR = '-'*75

    INVATION_MESSAGE = 'Введите номер элемета: '

    WRONG_INPUT_TYPE_MESSAGE = " <!> Введённые данные не являются цифрой. Завершение изменений <!> "

    WRONG_ELEMENT_NUM_MESSAGE = " <!> Такого элемента не существует. Попробуйте вновь <!> "

    def __init__(self, data: Union[list, dict]):
        ''' В виде данных допустимы : список, словарь
        для списка  : содержание элемента выводиться полностью
        для словаря : выводится только ключ
        '''
        self.is_dict = isinstance(data, dict)
        changable_seq = data
        if self.is_dict:
            changable_seq = data.keys()

        self.element_list = self.ElementList(changable_seq)
        self.base_data = data

    def run(self):
        print(self.SEPARATOR)
        print(self.INIT_MESSAGE)
        print(self.SEPARATOR)
        while True:
            elements__status = str(self.element_list)
            backwards_steps = len(re.findall('\n', elements__status))
            print(self.element_list)
            print(self.SEPARATOR)
            try:
                num = int(input(self.INVATION_MESSAGE))
            except ValueError:
                print(self.WRONG_INPUT_TYPE_MESSAGE)
                break
            backwards_steps += 4
            try:
                self.element_list.change_status_for_num(num)
            except self.ElementList.ElementNotFound:
                print(self.WRONG_ELEMENT_NUM_MESSAGE)
                backwards_steps += 1
                continue
            print(self.SEPARATOR)
            #print('\033[F\r\033[K')
            #print('\r'+'\033[K\033[F'*backwards_steps)
            # по идее нужна одельная консоль
        print(self.SEPARATOR)

        self.result_data = self.element_list.chosen_ones()
        if self.is_dict:
            self.result_data = { key: self.base_data[key] for key in self.result_data }

    def get_result(self):
        return self.result_data



class ModuleNames(list):
    '''
    {'name':str, 'type': 'module' | 'class' | 'method' | 'field' | 'function' }
    '''
    class ModuleNameElement:
        def __init__(self, name, type):
            self.name = name
            self.type = type

        @staticmethod
        def get_preffix_by_type(type):
            preffix = ''
            if type == 'class':
                preffix = '1.'
            elif type == 'method':
                preffix = '1.1.'
            elif type == 'field':
                preffix = '1.2.'
            elif type == 'function':
                preffix = '2.'
            return preffix

        def __str__(self, sep = ';'):
            return f'{self.get_preffix_by_type(self.type)}{sep}{self.name}'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.per_submodule_names = []

    def add_names_obj (self, obj):
        self.per_submodule_names.append( obj )

    def add_names(self, name, type):
        self.per_submodule_names.append(
                self.ModuleNameElement(name,type)
            )

    def add_module(self):
        '''храниться с внутренней метаинформацией,
        от которой стоит избавиться при передаче во вне'''
        self.append(self.per_submodule_names.copy())
        self.per_submodule_names.clear()

    def resize_by_a4_ratio(self, acess_string = lambda x: str(x), **kwargs):
        tmp = DimArray.get_dimmed_ratio( self, acess_string , **kwargs)
        self.clear()
        self += tmp

    def get_csv(self):
        return '\n'.join([';'.join([str(item) for item in module_items]) for module_items in self])

    def copy(self):
        return ModuleNames(super().copy())


class Serializable__Mixin:
    OBJ_NAME = 'DependenceCollector.ser'
    _is_loaded = False # чтобы не перезабивал уже десерилизованные поля по 5му протоколу

    def __new__(cls,
                *args,
                prepath: pathlib.Path = pathlib.Path(''),
                f__force_reinitialization=False,
                **kwargs):
        obj = super().__new__(cls)
        target_path = prepath / cls.OBJ_NAME
        cls._is_loaded = False
        if target_path.exists() and not f__force_reinitialization:
            byte_data = target_path.read_bytes()
            obj = pickle.loads(byte_data)
            cls._is_loaded = True
        return obj

    def __init__(self,
                 *args,
                 prepath: pathlib.Path = pathlib.Path(''),
                 f__force_reinitialization=False,
                 **kwargs):
        if not self._is_loaded:
            super().__init__(*args, **kwargs)
        self.target_path = prepath / self.OBJ_NAME
        self.f__force_reinitialization = f__force_reinitialization

    def serialize(self):
        ''' записывает объект в виде Pickle объекта по целевому пути
        :return: статус выполнения
        '''
        byte_data = pickle.dumps(self)
        if not self.target_path.exists() or self.f__force_reinitialization:
            self.target_path.write_bytes(byte_data)
            return 0
        return -1