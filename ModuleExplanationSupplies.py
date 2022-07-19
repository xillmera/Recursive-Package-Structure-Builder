import pathlib
import pkgutil
import io
import sys
import json
from typing import Union

from util import ModuleNames
from DiagramBuilder import Graph_XML_builder
from DependencesCollector import SerializableDependenceCollector

from Analisys import ModuleAnalisys
from RecursiveDataCollectors import GraphCollector, NamesCollector, IndicatorsCollector

class ModuleExplanationSupplies:
    ''' формирование файлов специальных форматов
    направленных на описание : одного модуля
    Сначала анализирует модуль,
    затем формирует всевозможные описывающие материалы
    - диаграммы иеирархии пакетов и модулей
    - граф импорта модулей внутри пакета
        (с рассстановкой элеменов внутри yEd
        с помощью встроенных алгоритмов
        outsource
    - листы уникальных имен

    подцелью является снижении информационной перегрузки диаграмм
        - это одна из причин почему возможно такое различие диаграмм
        ведь возможно указать все связи на одной
        но тогда она не читаема...
    '''
    def __init__(self,
                 module_info: pkgutil.ModuleInfo,
                 prepath: pathlib.Path = pathlib.Path(''),
                 f__force_reinitialization = False,
                 f__no_tread = False):
        self.base_info = module_info

        self.target_path = prepath / f'{module_info.name}'
        split__target_path = self.target_path.absolute().parts
        amount_section__target_path = len(split__target_path)+1
        for curr_part in range(1,amount_section__target_path):
            # check if path is created. if not do it
            tmp_path = pathlib.Path('\\'.join(split__target_path[:curr_part]))
            if tmp_path.exists():
                continue
            tmp_path.mkdir()

        self.obj = None
        self.obj = SerializableDependenceCollector(module_info=module_info,
                                                   prepath=self.target_path,
                                                   f__force_reinitialization=f__force_reinitialization,
                                                   f__no_tread= f__no_tread)
        try:
            pass
        except:
            # broken_mobule
            return


        if f__force_reinitialization or not self.obj._is_loaded:
            self.obj.recursive__sub_modules_collector()
            self.obj.serialize()
        self.log_run_metadata()

        self.graph_builer_obj = Graph_XML_builder()



    def log_run_metadata(self):
        output : io.TextIOWrapper = sys.stdout
        tmp_1p = json.dumps(list(self.obj.process_indicators['uninstalled']),indent="\t").replace('\n','\n\t\t')
        tmp_2p = json.dumps(list(self.obj.process_indicators['interactive']),indent="\t").replace('\n','\n\t\t')
        message = f'''
    сводка по выполнению ({self.base_info.name})
        uninstalled_modules : {tmp_1p}
        interactive_modules : {tmp_2p}
        '''
        output.write(message)

    # ответственность за хранение файлов и создание директории
    def log_uninstalled(self):
        tmp_path = (self.target_path / 'uninstalled_modules').with_suffix('.json')
        tmp_path.write_text(json.dumps(list(self.obj.process_indicators['uninstalled']),indent='\t'), encoding='utf-8')

    def log_interactive(self):
        tmp_path = (self.target_path / 'interactive_modules').with_suffix('.json')
        tmp_path.write_text(json.dumps(list(self.obj.process_indicators['interactive']),indent='\t'), encoding='utf-8')

    def hardness__signature(self, is_zipped = False, sep = ';') -> Union[list, str]:
        ''' возвращает сигнатуру содержащую
        информацию о количестве уникальных имен
        элементов разных типов метода в следующем порядке:
        - количество подмодулей
        - имя
        - кол. классов
        - кол. методов
        - кол. полей
        - кол. функций
        _ is_zipped _ (bool) : возможно перевести сразу в str
            используя _ sep _ (str)
        '''
        # для использования в AllAvaluablePackagesExplanationSupplies
        collector = IndicatorsCollector()
        self.obj.recursive__executor(
            data_processing_callback=collector.base
        )
        mainfest, indicators = collector.obj.get_only_internal_data()

        filesystem = set(self.obj.process_indicators['filesystem'])
        not_test_filesystem = set([item for item in filesystem if not 'test' in item])
        filesystem_amount = len(filesystem)
        tests_amount = len(filesystem.difference(not_test_filesystem))
        not_test_filesystem_amount = filesystem_amount - tests_amount

        inside_module = set(self.obj.process_indicators['inside_module'])
        inside_module_without_filesystem_amount = len(inside_module.difference(filesystem))
        sign = [
            not_test_filesystem_amount,
            tests_amount,
            inside_module_without_filesystem_amount,
            self.base_info.name,
        ] + indicators
        sign = [sum(sign[0:3]), *sign, sum(sign[4:])]
        if is_zipped:
            sign = sep.join(map(str,sign))
        return sign



    def ierarchic__mode__graph_builder(self, graph_save_mode) -> None:
        '''на вход приходит одна из функций-collector из GraphSaver'''
        assert graph_save_mode.__name__ in GraphCollector.__dict__
        self.obj.recursive__executor(
            data_processing_callback=graph_save_mode
        )
        tmp_path = (self.target_path / graph_save_mode.__name__).with_suffix('.graphml')
        tmp_path.write_text(GraphCollector.get_XML(), encoding='utf-8')

    def ierarchic__names_sheet__compliter(self, **kwargs) -> ModuleNames:
        ''' сохраняет все имена в порядке следования модулей
        далее записывает их в виде csv с a4 масштабированием строки'''
        self.obj.recursive__executor(
            data_processing_callback=NamesCollector.base
        )
        names__obj__before_changes = NamesCollector.obj.copy()
        NamesCollector.obj.resize_by_a4_ratio(**kwargs)
        csv_cont = NamesCollector.obj.get_csv()
        tmp_path = (self.target_path / 'names_sheet').with_suffix('.csv')
        tmp_path.write_text(csv_cont, encoding='utf-8')
        return names__obj__before_changes


class Test2:
    def v1(self):
        import traceback
        mod_info = None
        mod_name = 'numpy'
        #mod_name = 'csv'
        for item in pkgutil.iter_modules():
            if item.name == mod_name:
                mod_info = item
                break
        '''
        for item in pkgutil.iter_modules([mod_info.module_finder.path+'\\numpy']):
            if item.name == 'lib':
                mod_info = item
                break

         '''
        if mod_info is None:
            raise ValueError('usr. Нет такого модуля')
        tmp = True
        tmp = False
        '''
        while True:
            md_obj = ModuleExplanationSupplies(mod_info, f__force_reinitialization=tmp)
            tmp = False'''
        md_obj = ModuleExplanationSupplies(mod_info, f__force_reinitialization=tmp)
        md_obj.log_uninstalled()
        md_obj.log_interactive()
        sig = md_obj.hardness__signature()
        md_obj.ierarchic__mode__graph_builder(GraphCollector.NonOverlappingImport)
        md_obj.ierarchic__mode__graph_builder(GraphCollector.InnerCrossImport)
        #md_obj.ierarchic__names_sheet__compliter()


if __name__ == '__main__':
    tst = Test2()
    tst.v1()