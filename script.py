import pathlib
import pkgutil
import sys

from util import CLI_ChoseExceptionData, time_mesurement, ModuleNames
from ModuleExplanationSupplies import ModuleExplanationSupplies
from RecursiveDataCollectors import GraphCollector

class AllAvaluablePackagesExplanationSupplies:
    '''формирование файлов специальных форматов
    направленных на описание : всех доступных модулей в системе

    - лист всех доступных неповрежденных модулей со сложностью / индикаторами
        сложность - некая абстрактная характеристика зависящая от количества
        уникальных имён в пакете

    сделать проверку (остановку) необходимости анализа всех путей
        чтобы можно было вычекнуть некоторые
    '''
    def __init__(self, exception_names_list = None):
        self.prepath = pathlib.Path('production')
        if exception_names_list is None:
            exception_names_list = list()
        self.exception_names_list = exception_names_list

        self.total_names = ModuleNames()
        self.total_names_extended = ModuleNames()

    def path_correct_by_interface(self):
        cli = CLI_ChoseExceptionData(self.pathes)
        cli.run()
        self.pathes = cli.get_result()

    @property
    def pathes(self):
        if not '_pathes' in self.__dict__:
            self._pathes = sys.path
        return self._pathes

    @pathes.setter
    def pathes(self, value: list):
        if not isinstance(value, list):
            raise TypeError
        self._pathes = value

    @property
    def all_avaluable_modules(self):
        if not '_all_avaluable_modules' in self.__dict__:
            self._all_avaluable_modules = [mod for mod in pkgutil.iter_modules(self.pathes)]
        return self._all_avaluable_modules


    def collect_all_modules_info(self, f__force_reinit=False, limit = 'Infinity'):
        idx = 0
        limit = float(limit)
        for module_info in self.all_avaluable_modules:
            if module_info.name in self.exception_names_list:
                continue
            idx += 1
            if idx >= limit:
                break

            self.module_info__collector(module_info=module_info,
                                        f__force_reinit=f__force_reinit)

    def collect_one_module_info(self, module_name, f__force_reinit=False,f__no_tread = False):
        for module_info in self.all_avaluable_modules:
            if not module_info.name == module_name:
                continue
            self.module_info__collector(module_info=module_info,
                                        f__force_reinit=f__force_reinit,
                                        f__no_tread = f__no_tread)
            break

    def module_info__collector_strip(self, module_info): # temporary
        md_obj = ModuleExplanationSupplies(module_info,
                                           prepath=self.prepath)
        self.total_names += md_obj.hardness__signature(True)
        self.total_names_extended += md_obj.ierarchic__names_sheet__compliter()

    @time_mesurement
    def module_info__collector(self, module_info, f__force_reinit = False, f__no_tread = False):
        md_obj = ModuleExplanationSupplies(module_info,
                                           prepath=self.prepath,
                                           f__force_reinitialization=f__force_reinit,
                                           f__no_tread = f__no_tread)
        md_obj.log_uninstalled()
        md_obj.log_interactive()
        self.total_names.append(md_obj.hardness__signature())
        md_obj.ierarchic__mode__graph_builder(GraphCollector.NonOverlappingImport)
        #md_obj.ierarchic__mode__graph_builder(GraphCollector.InnerCrossImport)
        #md_obj.ierarchic__mode__graph_builder(GraphCollector.ClassCrossImport)
        #md_obj.ierarchic__mode__graph_builder(GraphCollector.ClassUniqueImport)
        #md_obj.ierarchic__mode__graph_builder(GraphCollector.ClassUniqueWithMroImport)
        #md_obj.ierarchic__mode__graph_builder(GraphCollector.ClassUniqueStripWithMroImport)
        #md_obj.ierarchic__mode__graph_builder(GraphCollector.ClassExtendedInfo) # опыты пока дошел
        md_obj.ierarchic__mode__graph_builder(GraphCollector.ClassExtendedInfoWithIerarchic)

        all_names = md_obj.ierarchic__names_sheet__compliter()
        self.total_names_extended += md_obj.ierarchic__names_sheet__compliter(down_pages = 2)
        pass




    def save_total_names_base(self):
        class GetIndicator:
            is_mod = False

            @classmethod
            def unify (cls, item):
                tmp = item.copy()
                mod_am = tmp[0]+tmp[1]
                names_am = sum(tmp[3:])
                if cls.is_mod:
                    return mod_am
                else:
                    return names_am

        self.total_names.sort(key=GetIndicator.unify)
        for idx in range(len(self.total_names)):
            self.total_names[idx] = ';'.join(map(str,self.total_names[idx]))

        self.save_total_names(self.total_names, '__base')

    def save_total_names(self, obj, specifier:str = ''):
        names__obj = obj.copy()
        names__obj.resize_by_a4_ratio()
        csv_cont = names__obj.get_csv()
        tmp_path = (self.prepath / ('names_sheet'+specifier)).with_suffix('.csv')
        tmp_path.write_text(csv_cont, encoding='utf-8')

class AllAvaluablePackagesExplanationSupplies__test:

    @classmethod
    @time_mesurement
    def v1 (self):

        exception_list = ['idlelib','test','crypto','kivy', 'pygments', 'serial','telethon','pywin',
                                  'tensorflow', 'torch', 'tqdm', 'twisted', 'win32com']

        interactive = ['tkinter']
        exception_list += interactive

        obj = AllAvaluablePackagesExplanationSupplies( exception_names_list=exception_list )
        obj.path_correct_by_interface()
        obj.collect_all_modules_info()
        obj.save_total_names_base()
        obj.save_total_names(obj.total_names_extended, '_total_extended')

    @classmethod
    @time_mesurement
    def v2 (self):
        target_name  = 'asyncio'.lower()
        obj = AllAvaluablePackagesExplanationSupplies()
        force_reinit = False
        force_reinit = True

        no_treads = True
        no_treads = False
        obj.collect_one_module_info(target_name, force_reinit, no_treads)
        pass # breakpoint to inspect structure

# todo сделать класс таблицы LibreOffice формата html

if __name__ == '__main__':
    #AllAvaluablePackagesExplanationSupplies__test.v1()
    AllAvaluablePackagesExplanationSupplies__test.v2()



