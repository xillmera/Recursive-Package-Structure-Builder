Запуск : script.py

# Описание
Модуль для сбора информации о модулях
    используется в связке с pkgutil.iter_modules() 
    на вход принимает имя модуля 
	который находит в результате сканирования из всех доступных. 
	
Интерактивного выбора модуля нет. 
Необходимо вручную указать название в 154 стр.

# Исследование структуры
100 строка - breakpoint to inspect structure (md_obj.obj.filesystem_modules > рекурсия)
главный объект SerializableDependenceCollector наследует авто-серилизацию от Serializable__Mixin (utils)
	благодаря переопределению `__new__`

# Результат работы
Скрипт создает директорию production/ c подкаталогом <имя модуля>/ в расположении исходного кода
Доступны несколько файлов : 
- диаграммы : (подразумевается использвоание возможности прогарммы yEd diagramm editor по авто-расстановке элементов (все элементы расстановлены в нечитаемом порядке) наиболее всего зарекомендовал себя circular layout)
	- ClassExtendedInfoWithIerarchic.graphml
	- NonOverlappingImport.graphml
- names_sheet.csv (все имена встречающиеся в модуле отформатированные для печати на а4 и дальнейшей склейке листов)
- теже данные в текстовом структурированном виде
	- uninstalled_modules.json 
	- interactive_modules.json
- DependenceCollector.ser (авто-серилизованная структура по Pickle протоколу)

--- 

# Конец вывода

... (вывод пропущен) 

    сводка по выполнению (numpy)
        uninstalled_modules : [
			"numpy._typing._extended_precision",
			"numpy.f2py.setup",
			"numpy.core.cversions",
			"numpy.core.setup",
			"numpy.core.generate_numpy_api",
			"numpy._pyinstaller.hook-numpy"
		]
        interactive_modules : [
			"numpy.fft.tests",
			"numpy.linalg.tests",
			"numpy.tests",
			"numpy.array_api.tests",
			"numpy.lib.tests",
			"numpy.f2py.tests",
			"numpy.ma.testutils",
			"numpy.conftest",
			"numpy.core.tests",
			"numpy.core.umath_tests",
			"numpy.compat.tests",
			"numpy._pyinstaller.test_pyinstaller",
			"numpy.testing",
			"numpy._pytesttester",
			"numpy.core._struct_ufunc_tests",
			"numpy.random.tests",
			"numpy.f2py.__main__",
			"numpy.core._umath_tests",
			"numpy.matrixlib.tests",
			"numpy.typing.tests",
			"numpy.core._rational_tests",
			"numpy.ma.tests",
			"numpy.core._operand_flag_tests",
			"numpy.core._multiarray_tests",
			"numpy.distutils.tests",
			"numpy.polynomial.tests"
		]
        1.3847734194496955 552 39.42857142857143 — A4 ratio params
20.7145746579417 205 14.642857142857142 — A4 ratio params # некоторые соотношения при размещении на листе
time_mesurement: выполнение module_info__collector заняло 216 sec
time_mesurement: выполнение v2 заняло 216 sec

Process finished with exit code 0