import abc
import io
import sys
import pathlib
import importlib
import pkgutil
import json
import traceback

from DiagramBuilder import Graph_XML_builder
from Analisys import ModuleAnalisys
from util import PrivateModuleError, ModuleNames, Serializable__Mixin, SingleTonSet


class DependencesCollector (dict):
    ''' Модуль для сбора информации о модулях
    используется в связке с pkgutil.iter_modules()
    на вход принимает объект выхода данной функции
    а именно : pkgutil.ModuleInfo
    '''
    PROBLEMATIC_PCKGS = ['tkinter.'] #todo
    # решает проблему разных экземпляров

    class NamesIndicators(dict):

        class FilesystemNames(SingleTonSet):pass
        class InsideModuleNames(SingleTonSet):pass
        class UninstalledModules(SingleTonSet):pass
        class InteractiveModules(SingleTonSet):pass

        _FULL_DICT = {
                'filesystem': FilesystemNames(),
                'inside_module': InsideModuleNames(),
                'uninstalled': UninstalledModules(),
                'interactive': InteractiveModules()
            }

        _CLEAR_DICT = {
            'filesystem': None,
            'inside_module': None,
            'uninstalled': None,
            'interactive': None
        }

        def __init__(self,
                     *args,
                     is_main = True,
                     **kwargs):
            super().__init__(*args,**kwargs)
            self.is_main = is_main
            self.clear()


        def clear(self) -> None:
            super().clear()
            if len(self) == 0:
                self.update(self._FULL_DICT)
            else:
                for key, item in self.items():
                    if item is None:
                       self[key] = self._FULL_DICT[key]


        def __reduce__(self):
            return (
                self.__class__,
                (dict(self),) if self.is_main else ( self._CLEAR_DICT, ) ,
                {'is_main':self.is_main}
            )

    class ModuleInfo:
        # возможно в сет добавлять не строки имен, а объект.
        # правда нужно скорее всего переопределять хеширование
        # в таком объекте
        pass

    _is_main_appeared = False

    # <~> initialization ---------------------------------------------------- <~>
    def __init__(self,
                 module_info: pkgutil.ModuleInfo = None,
                 f__no_tread: bool = False,
                 **kwargs):
        ''' Инициализация модуля имеет особенность
        в обычном случае происходит lazy-import
        для достоверной работы дальнейших функций его нужно обходить
        что и делается в данном блоке
        Если при полной загрузке модуль выдает ошибку
        скорее всего проблема с самим модулем,
        но не данным кодом,
        в частности это различия из за платформы исполнения
        
        аргументы : load_broken,is_package, mod_name, mod_file
        - нужны для де-сериализации 
        '''
        super().__init__(**kwargs)
        if self.__len__() == 0:
            self.clear()

        self.mod_info = module_info
        #if not module_info is None:
        self.is_package = module_info.ispkg
        if not DependencesCollector._is_main_appeared:
            DependencesCollector._is_main_appeared = True
        self.f__no_tread = f__no_tread
        # <!> поля состояния объекта
        # load_broken: bool = False,
        # is_package: bool = False,
        # mod_name: str | None = None,
        # mod_file: str | None = None,



    def clear(self) -> None:
        super().clear()
        self.update({
            'process_indicators': self.NamesIndicators(is_main=not self._is_main_appeared),
            'internal_info': ModuleAnalisys(),
            'filesystem_modules': dict(),
        })


    def __reduce__(self):
        return (self.__class__, 
                ( self.mod_info, ), {'module_info': self.mod_info, #active field
                 'load_broken' : self.load_broken if 'load_broken' in self.__dict__ else True,
                 'is_package'  : self.is_package, #active field - в целом не обязательно сохранять
                 'mod_name'    : self.mod_name if 'mod_name' in self.__dict__ else None,
                 'try_mod_name': self.try_mod_name if 'try_mod_name' in self.__dict__ else None,
                 'mod_file'    : self.mod_file if 'mod_file' in self.__dict__ else None},
                None,  iter(self.items()))
                # None - значит нет информации
    '''
    def __setstate__(self, state):
        self.mod_info = state['module_info']
        self.load_broken = state['load_broken']
        self.is_package = state['is_package']
        self.mod_name = state['mod_name']
        self.mod_file = state['mod_file']
    '''
    # <!> active funcs -------------------------------------------------------- <!>
    
    def load_obj (self, parent_module_name = None):
        tmp_io = None
        tmp_obj = None
        self.load_broken = False
        try:

            name = self.mod_info.name
            if parent_module_name:
                name = f'{parent_module_name}.{name}'
            message = f'try to load : {name}'
            sys.stdout.write('[ ] '+message)
            self.try_mod_name = name # для логики указания несработавших

            # на время импорта изолировать вывод
            tmp_io = io.StringIO()
            stdout_isolated = sys.stdout
            sys.stdout = tmp_io

            if '__main__' in name:
                #raise NameError # наиболее вероятно что интерактивный модуль
                raise SystemExit # обычно характерна интерактивному модулю
            if 'test' in name :
                raise SystemExit # обычно тесты не стоят того чтобы их запускать


            fndr = self.mod_info.module_finder
            spec = fndr.find_spec(name)
            tmp_obj = importlib.util.module_from_spec(spec)
            #self.mod_name =  self.obj.__name__
            loader = tmp_obj.__loader__
            try:
                try:
                    loader.exec_module(tmp_obj)
                except (ModuleNotFoundError, ImportError, NameError, KeyError):
                    #loader.load_module()
                    # different import module technic
                    # numpy.lib → numpy.lib.type_check (NameError)
                    # numpy.testing.tests.test_utils -> KeyError
                    obj = importlib.import_module(name)
                    pass # debug_purposes
                stdout_isolated.write('\r[x] '+message)
            except KeyError:
                # opt_einsum raises
                raise
            except NameError:
                # h11, base58 raises
                # ssl raises - _SSLMethod missing
                raise
            self.mod_name = tmp_obj.__name__ if '__name__' in tmp_obj.__dict__ else None
            self.mod_file = tmp_obj.__file__ if '__file__' in tmp_obj.__dict__ else None
            # tmp = self.obj.__dict__
            pass # debug_purposes
        except (ModuleNotFoundError, ImportError, NameError):
            # как оказалось - список был сделан по 3.10, а код запускался на 3.9
            # отсюда ModuleNotFoundError
            # tty raises (terminos missing)
            # curses raises (_curses missing)
            # crypt raises (_crypt missint)
            # pybrain raises (structure missing)
            # smplx raises (torch missing)
            # numpy raises (seamlessly) (pytest missing)
            # numpy.lib raises (type_check missing)
            # если пакет выдает ошибку - скорее всего он сломан
            # в частности, вышеперечисленные примеры приходят из
            # различий ос, проблемы мультиплатформенности

            # потенциально... если модуль сломан, то нужна другая стратегия
            # получения информации - к примеру, физический проход по коду без импорта
            # но это задача по сути мимикрирование функций интерпретатора
            # по распознаванию конструкций
            # в простом случае - это просто импорт
            # (для которого есть модуль - SimpleImportHelper или как его)
            raise
        except SystemExit:
            # numpy.f2py raises = exit() statement in importing code
            raise
        except:
            traceback.print_exc()
            self.load_broken = True
        finally:
            tmp_io.close()
            sys.stdout = sys.__stdout__
            sys.stdout.write('\n')
        return tmp_obj

    # __all__ potintial analisys
    def recursive__sub_modules_collector(self,
                                         parent_module_name = None,
                                         **kwargs) -> None:
        ''' Рекурсивный проход по файловой структуре модуля
        подмодули находятся с помощью pkgutil.iter_modules()
        возвращает:
         - уникальные имена всех подмодулей
         - количество ункикальных имен использованных модулей
            (в том числе *side)

        результат работы не возвращается непосредственно
        '''
        try:
            # Меры сохранения памяти... (загрузить и сгрузить до начала рекурсии)
            obj = self.load_obj(parent_module_name=parent_module_name)

            # для любого файла собираются зависимости внешние.
            module_analisys = ModuleAnalisys(**kwargs)
            module_analisys.update_module_info(obj)
            if self.f__no_tread:
                module_analisys.get_referenced_modules_from_module_obj()
            else:
                module_analisys.threaded__get_referenced_modules_from_module_obj()
            self['internal_info'] = module_analisys
            for mod_obj, _, is_sub, is_public in \
                    module_analisys.get_sub_modules_from_target__iterator(self.mod_name):
                if not is_public or is_sub:
                    continue
                # на (сложность) количество модулей влияют только уникальные внешние зависимости
                curr__mod_name = mod_obj['hierarchy_name']
                #if not curr__mod_name in self.process_indicators['filesystem']:
                # бессмысленно . ибо может встретиться раньше чем рекурсия дойдет до одноименного
                # файла-модуля . проще исключить пересечение
                self.process_indicators['inside_module'].add(curr__mod_name)
        except (ModuleNotFoundError, ImportError, NameError):
            # нужно подгрузить модуль (отдельный список)
            # может работать с импортом из необязательных модулей
            # поэтому при установке через pip может не хватать зависимостей.
            # в этом случае они записываются в список.
            self.process_indicators['uninstalled'].add(self.try_mod_name) # сохраняет пробуемое к импотру имя (до самого импорта)
        except SystemExit:
            self.process_indicators['interactive'].add(self.try_mod_name)
        except AttributeError:
            print(self.get_module_name(self))

        self.is_package = self.mod_info.ispkg
        if self.is_package and 'mod_file' in self.__dict__ and self.mod_file \
                and (mod_path:= pathlib.Path(self.mod_file).parent)\
                and not (found_modules:= pkgutil.iter_modules([mod_path])) is None:
                #не ошибка оказывается. можно поменять обратно
            for inf_mod in found_modules:

                tmp_dep_col = DependencesCollector( module_info= inf_mod )
                # если модель битый это станет ясно при инициализации головного __init__
                # можно сделать возврат отдельного "битого" объекта-класса
                tmp_dep_col.recursive__sub_modules_collector(
                    parent_module_name=self.mod_name
                )
                try:
                    found_mod__name = tmp_dep_col.mod_name
                except AttributeError:
                    # значит состояние не изменилось за время load_obj
                    # косвенно значит, что объект не удалось загрузить
                    found_mod__name = tmp_dep_col.try_mod_name

                self.process_indicators['filesystem'].add(found_mod__name)
                self['filesystem_modules'].update({found_mod__name: tmp_dep_col})

    # <> passive data access -------------------------------------------------- <>

    @property
    def internal_info(self):
        return self['internal_info']

    @property
    def process_indicators(self):
        return self['process_indicators']

    @staticmethod
    def get_module_name ( exem ):
        '''Защищено от случаев, когда не удалось загрузить модуль
        на вход подается экземпляр данного класса
        '''
        if exem is None:
            raise TypeError
        elif 'mod_name' in exem.__dict__ and not exem.mod_name is None:
            return exem.mod_name
        else:
            return exem.try_mod_name

    def sub_file_packages(self) -> tuple:
        ''' Итератор по вложенным модулям
        возвращает :
        - объект DependanceCollector для модуля
        - является он подпакетом (True) или подмодулем (False)
        - ierarchic имя пакета
        '''
        for mod_name, dep_col_obj in self['filesystem_modules'].items():
            yield dep_col_obj, dep_col_obj.is_package, mod_name


    def recursive__executor(self, 
                            data_processing_callback = None, 
                            base_element = None ):
        ''' метод для рекурсивного прохода структуры с выполнением callback
        требование к callback одно : 
        - первым элементом или именованным "data" 
            должно принимать объект типа : DependansesCollector
        
        для сохранения памяти рекурсивная часть не передается.
        
        подразумевается что callback это метод уже готового экземпляра класса 
        для того чтобы результат исполнения сохранялся в независимом пространстве
        
        рекурсивный вызов происходит до последнего элемента в ветви
        '''
        
        #memory update technique
        #tmp__recursive_element = self['filesystem_modules']
        #self['filesystem_modules'] = 'Blocked'
            
        if data_processing_callback:
            data_processing_callback(data = self, base_element = base_element)

        #for mod_name, filesystem_item in tmp__recursive_element.items():
        for filesystem_item, _, _ in self.sub_file_packages():
            filesystem_item.recursive__executor(
                data_processing_callback=data_processing_callback,
                base_element=self
            )
            try:
                pass
            except AttributeError:
                pass

        #self['filesystem_modules'] = tmp__recursive_element


class SerializableDependenceCollector(Serializable__Mixin, DependencesCollector):
    pass

class Test :
    def v1(self):
        from modules_getter import get_mods
        import json
        import traceback
        dct = {}
        for mod_name in get_mods():
            #obj = importlib.import_module(mod_name)
            #if mod_name in ['crypt', 'curses','pty','tty','termios','OpenGL']:
            #    continue
            try:
                dc = DependencesCollector(mod_name)
            except (PrivateModuleError, ModuleNotFoundError, ImportError):
                traceback.print_exc()
                continue
            _, modules_amount = dc.recursive__sub_modules_collector()
            tmp = {mod_name:{'modules_amount':modules_amount,'deps':dc.dependences}}
            dct.update(tmp)
            pass
        dct_lst = list(dct.items())
        dct_lst.sort(key= lambda x : x[1]['modules_amount'])
        with open('../production_2/modules_dependences.json', 'w', encoding='utf-8') as fl:
            json.dump(dct_lst, fl, indent='\t')

    def v2(self):
        import json
        dct = None
        with open('../production_2/modules_dependences.json', 'r', encoding='utf-8') as fl:
            tmp = fl.read()
            dct = json.loads(tmp)
        nw_lst = []
        for item in dct:
            tmp = {'name':item[0],'modules_amount':item[1]['modules_amount']}
            tmp = ';'.join(map(str,tmp.values()))
            nw_lst.append(tmp)

        row_el_am = 48
        resz_csv_arr = [[] for i in range(row_el_am)]
        shift = 0
        for idx, item in enumerate(nw_lst):
            if idx % row_el_am == 0:
                shift += 1
            resz_csv_arr[idx - (shift * row_el_am)].append(item)

        csv_cont_a4 = '\n'.join([';'.join(line) for line in resz_csv_arr])

        p = (pathlib.Path('../production_2/') / 'moduless_list').with_suffix('.csv')
        p.write_text(csv_cont_a4, encoding='utf-8')

    def v3(self):
        import traceback
        mod_info = None

        for item in pkgutil.iter_modules():
            if item.name == 'numpy':
                mod_info = item
                break
        if mod_info is None:
            raise ValueError
        try:
            dc = DependencesCollector(mod_info)
        except (PrivateModuleError, ModuleNotFoundError, ImportError):
            traceback.print_exc()
        _, modules_amount = dc.recursive__sub_modules_collector()
        print(modules_amount,dc.dependences)

    def v4(self):
        from modules_getter import iterator__over_modules_into_pathes
        import traceback

        broken_modules_list = []
        f_start = False
        for mod in iterator__over_modules_into_pathes():
            if mod.name == 'antigravity':
                continue #annoying after > 30 appears
            if mod.name == 'oauthlib':
                f_start = True
            if not f_start:
                continue
            try:
                dc = _DependencesCollector(mod)
            except : #(PrivateModuleError, ModuleNotFoundError, ImportError, NameError):
                traceback.print_exc()
                broken_modules_list.append(mod.name)
                continue
            print(mod.name)
            continue
            _, modules_amount = dc.recursive__sub_modules_collector(f__only_public=True)
            print(modules_amount, dc.dependences)
        print('broken_packages:',broken_modules_list)

    def v5(self):
        dp = DependencesCollector( module_info=None )
        pass


if __name__ == '__main__':
    tst = Test()
    tst.v5()