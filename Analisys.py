import inspect
import threading

from util import SerializableSet
# нужно делать все операции с объектом в одном месте.
# иначе это очень накладно по памяти
# ведь изначально возможно работает lazy_import
# https://wil.yegelwel.com/lazily-importing-python-modules/

class ModuleAnalisys(dict):
    def __init__(self,
                 init_value = None,
                 value_on: bool  = False,
                 additional_source: bool = True,
                 **kwargs):#, base_module:str = None):
        '''Проще подавать название модуля в виде единой строки
        '''
        super().__init__(init_value  or dict(), **kwargs)

        self.value_on = value_on
        self.additional_source= additional_source

        if len(self) == 0:
            self.clear()

        self.obj__info = None
        self.module_name = None
        self.module_type = None


    def update_module_info(self, object):
        '''Проблемная часть
        вызов __dict__ на модуле не всегда дает достоверный результат
        без вывода __repr__() до целевой операции сохранения
        вывод даёт варьируемое значение от 108 (чаще) до 157 (153, 1..)
        т/е работет нестабильно, что критично для автоматизации процесса
        и получения достоверных данных
        upd: из-за lazy import
        '''
        # must be loaded properly. lazy import problem exists
        self.obj__info = object.__dict__
        self.module_name = object.__name__
        try:
            self.module_type = 'side'
        except AttributeError:
            self.module_type = 'built-in'

    def clear(self) -> None:
        super().clear()
        self.update({
            'modules': [],
            'classes': [],
            'functions': [],
            'numeric_indicators': self.Indicators(),
            'unique_types': self.UniqueTypes()  # for bechavior analisys
        })

    def __reduce__(self):
        return self.__class__, (dict(self),self.value_on, self.additional_source )#,\
               #None, None, \
               #{'value_on':self.value_on, 'additional_source':self.additional_source}.items()


    class UniqueTypes(SerializableSet): pass

    class Indicators(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(
                *args, **kwargs
            )
            if self.__len__() == 0:
                self.clear()

        def clear(self) -> None:
            super().clear()
            self.update({
                'modules': 0,
                'classes': 0,
                'methods': 0,
                'fields': 0,
                'functions': 0,
                'up_modules': 0,
                'up_classes': 0,
            })

        def __add__(self, value):
            assert isinstance(value, ModuleAnalisys.Indicators)
            for key in value:
                self[key] += value[key]

        def get_only_internal_data(self):
            manifest = ['classes','methods','fields','functions']
            tmp = [self[key] for key in manifest]
            return manifest, tmp

        def __reduce__(self):
            return (self.__class__, (dict(self),))


    @property
    def indicators(self):
        return self['numeric_indicators']

    def get_indicators(self):
        return self['numeric_indicators']

    def get_modules_elements_names(self) -> tuple:
        '''генератор
        возвращает все (элементы) классы, поля, методы , функции
        и тип в виде имён
        '''
        for key, (proxy__key, name_key) in {
                                    #'modules':['module','hierarchy_name'],
                                    'classes':['class','name'],
                                    'functions':['function','name']
                                }.items():
            for item in self[key]:
                if key == 'classes':
                    for item_1v in item['methods']:
                        item_1v = item_1v['name']
                        yield item_1v, 'method'
                    for item_2v in item['fields']:
                        yield item_2v, 'field'
                item = item[name_key]
                yield item, proxy__key

    def get_modules__iterator(self):
        '''примитивная функция'''
        for module in self['modules']:
            yield module

    def get_sub_modules_from_target__iterator(self, module_name='') -> tuple:
        '''Возвращает список статического размера в 4 элемента
        1й - инфонесущий, (остальные bool-типа = внутренние проверки)
        2й - (проверка) является текущий модуль подмодулем 
            пришедшего в качестве аргумента
        3й - (проверка)  является текущий модуль подмодулем
            откуда была извлечена ссылка на текущий
        4й - (проверка) является текущий модуль публичным 
            (открытым для использования) 
        пример использования : 
        for item, check_1, check_2, check_3 \
            in some_obj.get_sub_modules_from_target():
        или for item, _, check_2, _ \ 
        (можно упустить проверки - если не нужны)
        '''
        for module in self['modules']:
            ref_module_name = module['hierarchy_name']
            yield (module,
                  ref_module_name.startswith(module_name), #module_name in ref_module_name
                  module['hierarchy_type'] == 'sub',
                  module['access_modifier'] == 'public')

    def get_classes_info(self):
        '''
        :return:
        - name,
        - module,
        - mro,
        - methods
        - fields
        '''
        for class_info in self['classes']:
            yield (class_info['name'],
                   class_info['module_name'],
                   class_info['mro'],
                   class_info['methods'],
                   class_info['fields'])

    def get_classes(self):
        ''' все данные о классе
        '''
        for class_info in self['classes']:
            yield class_info

    def get_functions(self):
        ''' лучше не менять сигнатуру.
         так словарь позволяет получить
        только что нужно если нужно
        '''
        for func in self['functions']:
            yield func

    # ------------------------------------------------------active duties

    def _type__collector(self, name, obj):
        tmp = str(type(obj))
        if not tmp in self['unique_types']:
            self['unique_types'].add(tmp)

    def _get_dict_mro(self, obj):
        '''возвращает иерархию наследования
        в виде структуры данных:
        [{
            'name':str,
            'module':str
        }, ...]
        цель - абстагирование от внутреннего представления классов
        '''
        try:
            tmp = inspect.getmro(obj)
        except NameError:
            tmp = []
        mro = []
        for item in tmp:
            mro.append({
                    'name':item.__name__,
                    'module':item.__module__
                })
        return mro

    # потециал отнаследоваться от абстрактного класса
    def module__identifier(self, name, obj):
        '''Структура данных репрезентующая один модуль
        {
                           'type':'module'
                           'name': str  (_api)
                 'hierarchy_name': str  (matplotlib._api)
                 'hierarchy_type':      'sub' | 'up',
                    'supply_type':     'side' | 'built-in',
                'access_modifier':  'private' | 'public',
                          'value': < module > | None,
                           'path': str
        }
        '''
        if inspect.ismodule(obj) is False:
            return
        #print(name)
        value = None
        if self.value_on:
            value = obj
        dir(obj)
        tmp = {}
        tmp['type'] = 'module'
        tmp['name'] = name
        tmp['hierarchy_name'] = obj.__name__
        #tmp['hierarchy_type'] = 'sub' if '__package__' in dir(obj)\
        #        and self.module_name in obj.__package__ else 'up'
        # not stable - not all have properly setup __package__ protocol / some of them return None
        tmp['hierarchy_type'] = 'sub' if self.module_name in tmp['hierarchy_name'] else 'up'
        tmp['supply_type'] = 'side' if '__file__' in dir(obj) else 'built-in'
        tmp['access_modifier'] = 'private' if name.startswith('_') else 'public'
        tmp['value'] = value
        tmp['path'] = obj.__file__ if '__file__' in dir(obj) else None
        self['modules'].append(tmp)
        if tmp['hierarchy_type'] == 'sub':
            self.indicators['modules'] += 1
            #self['direct_links'].append(name)
        else :
            self.indicators['up_modules'] += 1

    def class__identifier (self, name, obj):
        '''Структура данных репрезентующая один класс
        {
                           'type':'class'
                           'name': str  (PostixPath)
                    'module_name': str  (Path)
                 'hierarchy_type':      'sub' | 'up',
                            'mro': [{ 'name': str, 'module': str}, ...]
                'access_modifier':  'private' | 'public',
                    'supply_type':     'side' | 'built-in',
                          'value': < class > | None,
                         'source': str,
             'source_line_amount':          0 | int
             'source_char_amount':          0 | int
                    'source_file': str ('c:\\somedir\\somedir\\__init__.py')
                        'methods':list(str)
                          'field': list(str)
        }
        '''
        if not inspect.isclass(obj): return
        tmp = {}
        dct = obj.__dict__
        dr = dir(obj)

        tmp['type'] = 'class'
        tmp['name'] = name
        tmp['module_name'] = obj.__module__
        tmp['hierarchy_type'] = 'sub' if self.module_name in tmp['module_name']  else 'up'
        tmp['mro'] = self._get_dict_mro(obj)
        tmp['access_modifier'] ='private' if name.startswith('_') else 'public'
        if self.value_on:
            tmp['value'] = obj
        tmp['supply_type'] = 'side'
        tmp['source_line_amount'] = 0
        tmp['source_char_amount'] = 0
        if self.additional_source:
            try:
                tmp['source'] = inspect.getsource(obj)
                tmp['source_file'] = inspect.getsourcefile(obj)
                tmp['source_line_amount'] = len(tmp['source'].split('\n'))
                tmp['source_char_amount'] = len(tmp['source'])
            except (OSError, TypeError):
                tmp['source'] = None
                tmp['source_file'] = None
                tmp['supply_type'] = 'built-in'
        tmp['methods'] = []
        for name, obj in dct.items():
            mtd_info = self.function__identifier(name, obj, tmp['name'])
            if mtd_info:
                tmp['methods'].append(mtd_info)
            if tmp['hierarchy_type'] == 'sub':
                self.indicators['methods'] += 1

        tmp['fields'] = [item for item, obj in dct.items()
                         if inspect.isdatadescriptor(obj)]

        if tmp['hierarchy_type'] == 'sub':
            self.indicators['fields'] += len(tmp['fields'])
            self.indicators['classes'] += 1
        else :
            self.indicators['up_classes'] += 1

        self['classes'].append(tmp)
        del tmp

    def function__identifier (self, name, obj, from_class=None):
        '''принадлежность классу определяется только из __dict__ самого класса
        Структура данных репрезентующая одну функцию
        {
                           'type':'func' | 'method'
                           'name': str  (touch)
                    'module_name': str  (Path) | None
                     'class_name': str  (PostixPath) | None
                'access_modifier':  'private' | 'public',
                    'supply_type':     'side' | 'built-in',
                          'value': < func > | None,
                         'source': str,
             'source_line_amount':          0 | int
             'source_char_amount':          0 | int
                    'source_file': str ('c:\\somedir\\somedir\\__init__.py')
        }
        бывают разные типы...
        -
        '''
        if from_class is None :
            if not inspect.isfunction(obj) and not inspect.isbuiltin(obj):
                return
        elif not inspect.ismethoddescriptor(obj) and not inspect.isfunction(obj):
            return
        tmp = {}
        tmp['name'] = name
        if from_class:
            tmp['type'] = 'method'
        else :
            tmp['type'] = 'func'
        if from_class is None:
            try:
                tmp['module_name'] = obj.__module__
            except AttributeError:
                return
        #    tmp['hierarchy_type'] = 'sub' if self.module_name in tmp['module_name'] else 'up'
        tmp['class_name'] = from_class
        tmp['access_modifier'] = 'private' if name.startswith('_') else 'public'
        if self.value_on:
            tmp['value'] = obj
        tmp['supply_type'] = 'side'
        if self.additional_source:
            try:
                tmp['source'] = inspect.getsource(obj)
                tmp['source_file'] = inspect.getsourcefile(obj)
                tmp['source_line_amount'] = len(tmp['source'].split('\n'))
                tmp['source_char_amount'] = len(tmp['source'])
            except (OSError, TypeError):
                tmp['source'] = None
                tmp['source_file'] = None
                tmp['supply_type'] = 'built-in'
        if from_class is None:
            self['functions'].append(tmp)
            self.indicators['functions'] += 1
            del tmp
        else :
            return tmp

    def _object_recognition_and_documentation(self, name):
        '''Классификация отдельного объекта
        метод обхода словаря указывается в прокси
        (из-за потенциала к многопоточности)
        по идее:
        срабатывает только одна из трех функций
        ниже получения объекта'''
        obj = self.obj__info[name] # получение объекта
        '''
        try:
            if inspect.ismodule(obj) and obj.__name__ in self.unique_names['filesystem']:
                return
        except AttributeError:
            pass
        '''
        self._type__collector(name, obj)
        self.module__identifier(name, obj)
        self.class__identifier(name, obj)
        self.function__identifier(name, obj)

    def get_referenced_modules_from_module_obj(self):
        '''обработка модулей -
        прокси автоклассификации
        обеспечивает линейность выполнения

        <!> активный объект - не подразумевается вызов без инишиализации имён
        (первичного построения, а не десерализация
        '''
        assert not self.obj__info is None #active object

        for name in iter(self.obj__info):
            self._object_recognition_and_documentation(name)
        del self.obj__info

    def threaded__get_referenced_modules_from_module_obj(self):
        '''обработка модулей -
        прокси автоклассификации
        обеспечивает многопоточность выполнения

        <!> активный объект - не подразумевается вызов без инишиализации имён
        (первичного построения, а не десерализация
        '''

        assert not self.obj__info is None #active object

        threads = []
        for name in iter(self.obj__info):
            new = threading.Thread(
                target=self._object_recognition_and_documentation,
                args=(name,)
            )
            threads.append(new)
            new.start()

        # если поток требует больше времени чем таймаут
        # то программа продолжаетсяч без окончания потока.
        # <!> возникает ошибка при дальнейшей логике удаления self.obj NoneTypeError
        #for thr in threads:
        #    thr.join()

        over_threads = iter(threads)
        curr_th = next(over_threads)
        while True:
            curr_th.join()
            if curr_th.is_alive():
                continue
            try:
                curr_th = next(over_threads)
            except StopIteration:
                break

        del self.obj__info

    #def __str__(self): # если всё лист - то нет проблем с json serialisation process

class Test:
    import pickle
    @staticmethod
    def v1():
        tmp = ModuleAnalisys.Indicators()
        data =  Test.pickle.dumps(tmp)
        obj =  Test.pickle.loads(data)
        pass

    @staticmethod
    def v2():
        tmp = ModuleAnalisys.UniqueNames({2213,323})
        data = Test.pickle.dumps(tmp)
        obj = Test.pickle.loads(data)
        pass

if __name__ == '__main__':
    Test.v2()

