from DiagramBuilder import Graph_XML_builder
from DependencesCollector import SerializableDependenceCollector
from Analisys import ModuleAnalisys
from util import ModuleNames

class GraphCollector:
    obj = Graph_XML_builder()
    ICI_base_mod = ''

    @classmethod
    def get_XML(cls):
        tmp = cls.obj.get_XML()
        cls.obj.clear()
        return tmp


    @classmethod
    def NonOverlappingImport(cls, data, base_element):
        '''collector
        удачная - показывает иерархию модулей
        '''
        gb = cls.obj
        try:
            gb.node_insert(
                SerializableDependenceCollector.get_module_name(data)#,
                #fontsize=120
            )
        except ValueError:
            # already exists
            pass
        except TypeError:
            return

        try:
            gb.create_edge_from_two_text_if_exist(
                SerializableDependenceCollector.get_module_name(base_element),
                SerializableDependenceCollector.get_module_name(data)#,
                #width= 40.0
            )
        except TypeError:
            return

    @classmethod
    def InnerOuterCrossImport(cls, data, base_element):
        '''collector'''
        gb = cls.obj
        try:
            data__mod_name = SerializableDependenceCollector.get_module_name(data)
        except TypeError:
            return

        if 'test' in data__mod_name or \
                data__mod_name.split('.')[-1].startswith('_'):
            return

        try:
            gb.node_insert(
                data__mod_name + ' (pr)',
                fontsize=10,
                f__unique_names=True

            )

            gb.node_insert(
                data__mod_name,
                fontsize=200,
                f__unique_names=True

            )


            gb.create_edge_from_two_text_if_exist(
                data__mod_name + ' (pr)',
                data__mod_name,
                width= 8.0
            )
        except ValueError:
            # already exists
            pass

        for module_data__internal, _, is_sub, _ in \
                data.internal_info.get_sub_modules_from_target__iterator(
                    data__mod_name
                ):
            if not is_sub:
                pass#continue

            target__module_name = module_data__internal['hierarchy_name']
            if 'test' in data__mod_name or \
                data__mod_name.split('.')[-1].startswith('_'):
                continue
            try:
                gb.node_insert(target__module_name + ' (pr)',
                               fontsize=10,
                                f__unique_names=True)

                gb.node_insert(
                    target__module_name,
                    fontsize=200,
                    f__unique_names=True

                )

                gb.create_edge_from_two_text_if_exist(
                    target__module_name + ' (pr)',
                    target__module_name,
                    width=8.0
                )
            except ValueError:
                #continue
                pass
            gb.create_edge_from_two_text_if_exist(
                data__mod_name + ' (pr)',
                target__module_name + ' (pr)',
                width= 8.0
            )


    @classmethod
    def InnerCrossImport(cls, data, base_element):
        '''collector'''
        gb = cls.obj
        try:
            data__mod_name = SerializableDependenceCollector.get_module_name(data)
        except TypeError:
            return
        if base_element is None:
            cls.ICI_base_mod = data__mod_name

        if 'test' in data__mod_name or \
                data__mod_name.split('.')[-1].startswith('_'):
            return

        try:
            gb.node_insert(
                data__mod_name,
                fontsize=12,
                f__unique_names=True
            )

        except ValueError:
            # already exists
            pass

        for module_data__internal, is_sub, _, _ in \
                data.internal_info.get_sub_modules_from_target__iterator(
                    cls.ICI_base_mod
                ):
            if not is_sub:
                continue

            target__module_name = module_data__internal['hierarchy_name']
            if 'test' in data__mod_name or \
                data__mod_name.split('.')[-1].startswith('_'):
                continue
            try:
                gb.node_insert(target__module_name,
                               fontsize=12,
                                f__unique_names=True)
            except ValueError:
                #continue
                pass
            gb.create_edge_from_two_text_if_exist(
                data__mod_name,
                target__module_name
            )

    @classmethod
    def ClassCrossImport(cls, data, base_element):
        '''collector'''
        gb = cls.obj
        try:
            data__mod_name = SerializableDependenceCollector.get_module_name(data)
        except TypeError:
            return
        if base_element is None:
            cls.ICI_base_mod = data__mod_name

        if 'test' in data__mod_name or \
                data__mod_name.split('.')[-1].startswith('_'):
            return

        try:
            gb.node_insert(
                data__mod_name,
                fontsize=12,
                f__unique_names=True,
                color='CC6600'
            )

        except ValueError:
            # already exists
            pass

        for name, module_name, mro, _, _ in data.internal_info.get_classes_info():
            if 'test' in name or \
                    name.split('.')[-1].startswith('_'):
                continue
            try:
                gb.node_insert(name,
                               fontsize=12,
                               f__unique_names=True)
            except ValueError:
                # continue
                pass
            gb.create_edge_from_two_text_if_exist(
                data__mod_name,
                name
            )


    @classmethod
    def ClassUniqueImport(cls, data, base_element):
        '''collector'''
        gb = cls.obj
        try:
            data__mod_name = SerializableDependenceCollector.get_module_name(data)
        except TypeError:
            return
        if base_element is None:
            cls.ICI_base_mod = data__mod_name

        if 'test' in data__mod_name or \
                data__mod_name.split('.')[-1].startswith('_'):
            return

        gb.node_insert(
            data__mod_name,
            fontsize=12,
            f__unique_names=True,
            color='CC6600'
        )
        elems = data.internal_info.get_classes_info()
        repeat_cntr = 1
        iter_avaluable = True
        try:
            name, module_name, mro, _, _ = next( elems )
            tmp_name = name
        except StopIteration:
            iter_avaluable = False

        while iter_avaluable:
            if not (
                        'test' in name
                        or
                        name.split('.')[-1].startswith('_')
                    ):
                try:
                    base_color = 'FFCC00'
                    if 'warning' in name.lower() or 'error' in name.lower():
                        base_color = '660000'
                    gb.node_insert(tmp_name,
                                   fontsize=12,
                                   f__unique_names=True,
                                   color=base_color)
                    repeat_cntr = 1
                except ValueError:
                    tmp_name = name+f'_{repeat_cntr}'
                    repeat_cntr += 1
                    continue
                gb.create_edge_from_two_text_if_exist(
                    data__mod_name,
                    tmp_name
                )
            try:
                name, module_name, mro, _, _ = next( elems )
                tmp_name = name
            except StopIteration:
                break

    @classmethod
    def ClassUniqueWithMroImport(cls, data, base_element):
        '''collector'''
        gb = cls.obj
        try:
            data__mod_name = SerializableDependenceCollector.get_module_name(data)
        except TypeError:
            return
        if base_element is None:
            cls.ICI_base_mod = data__mod_name

        if 'test' in data__mod_name or \
                data__mod_name.split('.')[-1].startswith('_'):
            return

        gb.node_insert(
            data__mod_name,
            fontsize=12,
            f__unique_names=True,
            color='CC6600'
        )
        elems = data.internal_info.get_classes_info()
        repeat_cntr = 1
        iter_avaluable = True
        try:
            name, module_name, mro, _, _ = next(elems)
            tmp_name = name
        except StopIteration:
            iter_avaluable = False

        while iter_avaluable:
            if not (
                    'test' in name
                    or
                    name.split('.')[-1].startswith('_')
            ):
                try:
                    base_color = 'FFCC00'
                    if 'warning' in name.lower() or 'error' in name.lower():
                        base_color = '660000'
                    gb.node_insert(tmp_name,
                                   fontsize=12,
                                   f__unique_names=True,
                                   color=base_color)
                    repeat_cntr = 1
                except ValueError:
                    tmp_name = name + f'_{repeat_cntr}'
                    repeat_cntr += 1
                    continue
                gb.create_edge_from_two_text_if_exist(
                    data__mod_name,
                    tmp_name
                )

                upper_inherited_class = mro[0]['name']
                try:
                    gb.node_insert(upper_inherited_class,
                                   fontsize=12,
                                   f__unique_names=True,
                                   color=base_color)
                except ValueError:
                    pass

                gb.create_edge_from_two_text_if_exist(
                    tmp_name,
                    upper_inherited_class
                )


            try:
                name, module_name, mro, _, _ = next(elems)
                tmp_name = name
            except StopIteration:
                break

    @classmethod
    def ClassUniqueStripWithMroImport(cls, data, base_element):
        '''collector
        Получается диаграмма, где
        - к модулю привязаны классы,
        - каждый класс ссылается на родителей
        * исключая тестовые, класс object
        * ошибки выделены красным, классы желтым, модули оранжевым
        '''
        gb = cls.obj
        try:
            data__mod_name = SerializableDependenceCollector.get_module_name(data)
        except TypeError:
            return
        if base_element is None:
            cls.ICI_base_mod = data__mod_name

        if 'test' in data__mod_name or \
                data__mod_name.split('.')[-1].startswith('_'):
            return

        FONTSIZE = 20
        FONTSIZE = 100
        FONTSIZE = 12

        gb.node_insert(
            data__mod_name,
            fontsize=FONTSIZE,
            f__unique_names=True,
            color='CC6600'
        )

        for name, module_name, mro, _, _ in data.internal_info.get_classes_info():
            if (
                    'test' in name
                    or
                    name.split('.')[-1].startswith('_')
            ):
                continue
            try:
                base_color = 'FFCC00'
                if 'warning' in name.lower() or 'error' in name.lower():
                    base_color = '660000'
                gb.node_insert(name,
                               fontsize=FONTSIZE,
                               f__unique_names=True,
                               color=base_color)
                gb.create_edge_from_two_text_if_exist(
                    data__mod_name,
                    name
                )
            except ValueError:
                continue

            try:
                upper_inherited_class = mro[1]['name']
                assert not upper_inherited_class == 'object'
                assert not upper_inherited_class == name

                try:
                    gb.node_insert(upper_inherited_class,
                                   fontsize=FONTSIZE,
                                   f__unique_names=True,
                                   color=base_color)
                except ValueError:
                    pass


                gb.create_edge_from_two_text_if_exist(
                    name,
                    upper_inherited_class
                )
            except (AssertionError, IndexError):
                pass

    @classmethod
    def ClassExtendedInfo(cls, data, base_element):
        '''collector - circular layout - organic disc (partition > style)
        Получается диаграмма, где
        - только классы и их поля
        - классы ссылаются на модули
        '''
        gb = cls.obj
        try:
            data__mod_name = SerializableDependenceCollector.get_module_name(data)
        except TypeError:
            return
        if base_element is None:
            cls.ICI_base_mod = data__mod_name

        if 'test' in data__mod_name or \
                data__mod_name.split('.')[-1].startswith('_'):
            return

        FONTSIZE = 12
        MODULE_COLOR = 'CC6600'
        METHOD_COLOR = 'CC66FF'
        FIELD_COLOR = '9999FF'
        BASE_ELEMENT_COLOR = 'FFCC00'
        ERROR_COLOR = '660000'

        gb.node_insert(
            data__mod_name,
            fontsize=FONTSIZE,
            f__unique_names=True,
            color=MODULE_COLOR
        )

        for func_info in data.internal_info.get_functions():
            tmp_name = func_info['name']
            if (
                    'test' in tmp_name
                    or
                    tmp_name.split('.')[-1].startswith('_')
                    or
                    func_info['access_modifier'] != 'public'
            ):
                continue
            try:
                gb.node_insert(tmp_name,
                               fontsize=FONTSIZE,
                               f__unique_names=True,
                               color=METHOD_COLOR)
            except ValueError:
                tmp_name = func_info['name'] + f" ({data__mod_name})"
                gb.node_insert(tmp_name,
                               fontsize=FONTSIZE,
                               f__unique_names=True,
                               color=METHOD_COLOR)
            try:
                gb.create_edge_from_two_text_if_exist(
                    data__mod_name,
                    tmp_name
                )
            except ValueError:
                pass

        for name, module_name, mro, methods, fields in data.internal_info.get_classes_info():
            if (
                    'test' in name
                    or
                    name.split('.')[-1].startswith('_')
            ):
                continue
            try:
                chosen_color = BASE_ELEMENT_COLOR
                if 'warning' in name.lower() or 'error' in name.lower():
                    chosen_color = ERROR_COLOR
                gb.node_insert(name,
                               fontsize=FONTSIZE,
                               f__unique_names=True,
                               color=chosen_color)
                gb.create_edge_from_two_text_if_exist(
                    data__mod_name,
                    name
                )
                for method in methods:
                    tmp_name = method['name']
                    if (
                            'test' in tmp_name
                            or
                            tmp_name.split('.')[-1].startswith('_')
                            or
                            method['access_modifier'] != 'public'
                    ):
                        continue
                    try:
                        gb.node_insert(tmp_name,
                                       fontsize=FONTSIZE,
                                       f__unique_names=True,
                                       color=METHOD_COLOR)
                    except ValueError:
                        tmp_name = method['name'] + f' ({name})'
                        gb.node_insert(tmp_name,
                                       fontsize=FONTSIZE,
                                       f__unique_names=True,
                                       color=METHOD_COLOR)
                    try:
                        gb.create_edge_from_two_text_if_exist(
                            name,
                            tmp_name
                        )
                    except ValueError:
                        pass

                for field in fields:
                    tmp_name = field
                    if (
                            'test' in tmp_name
                            or
                            tmp_name.split('.')[-1].startswith('_')
                    ):
                        continue
                    try:
                        gb.node_insert(tmp_name,
                                       fontsize=FONTSIZE,
                                       f__unique_names=True,
                                       color=FIELD_COLOR)
                    except ValueError:
                        tmp_name = field + f' ({name})'
                        gb.node_insert(tmp_name,
                                       fontsize=FONTSIZE,
                                       f__unique_names=True,
                                       color=FIELD_COLOR)
                    try:
                        gb.create_edge_from_two_text_if_exist(
                            name,
                            tmp_name
                        )
                    except ValueError:
                        pass

            except ValueError:
                continue

            try:
                upper_inherited_class = mro[1]['name']
                assert not upper_inherited_class == 'object'
                assert not upper_inherited_class == name

                try:
                    gb.node_insert(upper_inherited_class,
                                   fontsize=FONTSIZE,
                                   f__unique_names=True,
                                   color=chosen_color)
                except ValueError:
                    pass


                gb.create_edge_from_two_text_if_exist(
                    name,
                    upper_inherited_class
                )
            except (AssertionError, IndexError):
                pass


    @classmethod
    def ClassExtendedInfoWithIerarchic(cls, data, base_element):
        '''collector - circular layout - organic disc (partition > style)
        Получается диаграмма, где
        - только классы и их поля
        - классы ссылаются на модули

        удачная - довольно полная информация по именам
        '''
        gb = cls.obj
        try:
            data__mod_name = SerializableDependenceCollector.get_module_name(data)
        except TypeError:
            return
        if base_element is None:
            cls.ICI_base_mod = data__mod_name

        if 'test' in data__mod_name or \
                data__mod_name.split('.')[-1].startswith('_'):
            return

        FONTSIZE = 12
        MODULE_COLOR = 'CC6600'
        METHOD_COLOR = 'CC66FF'
        FIELD_COLOR = '9999FF'
        BASE_ELEMENT_COLOR = 'FFCC00'
        ERROR_COLOR = '660000'

        try:
            gb.node_insert(
                data__mod_name,
                fontsize=FONTSIZE,
                f__unique_names=True,
                color=MODULE_COLOR
            )
        except ValueError:
            pass

        try:
            gb.create_edge_from_two_text_if_exist(
                SerializableDependenceCollector.get_module_name(base_element),
                data__mod_name,
                f__unique_vals=True
            )
        except (TypeError, ValueError):
            pass

        for func_info in data.internal_info.get_functions():
            tmp_name = func_info['name']
            if (
                    'test' in tmp_name
                    or
                    tmp_name.split('.')[-1].startswith('_')
                    or
                    func_info['access_modifier'] != 'public'
            ):
                continue
            try:
                gb.node_insert(tmp_name,
                               fontsize=FONTSIZE,
                               f__unique_names=True,
                               color=METHOD_COLOR)
            except ValueError:
                tmp_name = func_info['name'] + f" ({data__mod_name})"
                gb.node_insert(tmp_name,
                               fontsize=FONTSIZE,
                               f__unique_names=True,
                               color=METHOD_COLOR)
            try:
                gb.create_edge_from_two_text_if_exist(
                    data__mod_name,
                    tmp_name,
                    f__unique_vals=True
                )
            except ValueError:
                pass

        for class_info in data.internal_info.get_classes():
            name, module_name, mro, methods, fields = (class_info['name'],
                                                       class_info['module_name'],
                                                       class_info['mro'],
                                                       class_info['methods'],
                                                       class_info['fields'])
            if (
                    'test' in name
                    or
                    name.split('.')[-1].startswith('_')
            ):
                continue
            # импортируемый класс может быть из другого подмодуля
            try:
                chosen_color = BASE_ELEMENT_COLOR
                if 'warning' in name.lower() or 'error' in name.lower():
                    chosen_color = ERROR_COLOR

                try:
                    gb.node_insert(name,
                                   fontsize=FONTSIZE,
                                   f__unique_names=True,
                                   color=chosen_color)
                except ValueError:
                    pass

                try:
                    gb.node_insert(module_name,
                                   fontsize=FONTSIZE,
                                   f__unique_names=True,
                                   color=MODULE_COLOR)
                except ValueError:
                    pass

                try:
                    gb.create_edge_from_two_text_if_exist(
                        module_name,
                        name,
                        f__unique_vals=True
                    )
                except ValueError:
                    pass

                for method in methods:
                    tmp_name = method['name']
                    if (
                            'test' in tmp_name
                            or
                            tmp_name.split('.')[-1].startswith('_')
                            or
                            method['access_modifier'] != 'public'
                    ):
                        continue
                    try:
                        gb.node_insert(tmp_name,
                                       fontsize=FONTSIZE,
                                       f__unique_names=True,
                                       color=METHOD_COLOR)
                    except ValueError:
                        tmp_name = method['name'] + f' ({name})'
                        gb.node_insert(tmp_name,
                                       fontsize=FONTSIZE,
                                       f__unique_names=True,
                                       color=METHOD_COLOR)
                    try:
                        gb.create_edge_from_two_text_if_exist(
                            name,
                            tmp_name,
                            f__unique_vals=True
                        )
                    except ValueError:
                        pass

                for field in fields:
                    tmp_name = field
                    if (
                            'test' in tmp_name
                            or
                            tmp_name.split('.')[-1].startswith('_')
                    ):
                        continue
                    try:
                        gb.node_insert(tmp_name,
                                       fontsize=FONTSIZE,
                                       f__unique_names=True,
                                       color=FIELD_COLOR)
                    except ValueError:
                        tmp_name = field + f' ({name})'
                        gb.node_insert(tmp_name,
                                       fontsize=FONTSIZE,
                                       f__unique_names=True,
                                       color=FIELD_COLOR)
                    try:
                        gb.create_edge_from_two_text_if_exist(
                            name,
                            tmp_name,
                            f__unique_vals=True
                        )
                    except ValueError:
                        pass

            except ValueError:
                continue

            try:
                upper_inherited_class = mro[1]['name']
                assert not upper_inherited_class == 'object'
                assert not upper_inherited_class == name

                try:
                    gb.node_insert(upper_inherited_class,
                                   fontsize=FONTSIZE,
                                   f__unique_names=True,
                                   color=chosen_color)
                except ValueError:
                    pass

                try:
                    gb.create_edge_from_two_text_if_exist(
                        name,
                        upper_inherited_class,
                        f__unique_vals=True
                    )
                except ValueError:
                    pass

            except (AssertionError, IndexError):
                pass


class NamesCollector:
    obj = ModuleNames()
    exceptions = dict()


    @classmethod
    def get_CSV(cls):
        tmp = cls.obj.get_csv()
        cls.obj.clear()
        return tmp

    @classmethod
    def only_modules(cls, data, base_element):
        cls.obj.add_names(
            SerializableDependenceCollector.get_module_name(data),
            'module'
        )

    @classmethod
    def base(cls, data, base_element):
        cls.obj.add_names(
            SerializableDependenceCollector.get_module_name(data),
            'module'
        )

        for el_name, el_type in data.internal_info.get_modules_elements_names():
            if el_name.startswith('_'):
                continue
            new_el_name = el_name
            if el_name in cls.exceptions:
                amount = cls.exceptions[el_name]
                new_el_name += f' ({amount})'
                cls.exceptions[el_name]+=1
            else :
                cls.exceptions[el_name]=1
            el_name = new_el_name

            cls.obj.add_names(el_name, el_type)
        cls.obj.add_module()

class IndicatorsCollector:
    def __init__(self):
        self.obj = ModuleAnalisys.Indicators()

    def base(self, data, base_element):
        '''для использования в recursive__executor'''
        self.obj + data.internal_info.indicators

