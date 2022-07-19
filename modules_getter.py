import pkgutil as pkg
import pkgutil
import sys, json

# проблема в том, что запуск из PyCharm расширяет sys.path
 # внутренними пакетами self.iter__modules = pkgutil.iter_modules()
# поэтому нужно запускать отдельно
# можно исключить промежуточное звено в виде файла ...

# - как вариант сохранить sys.path и проходить по ним через генератор

def save_python_path():
    with open('../production_2/pythonpath.json','w',encoding='utf-8') as fl:
        json.dump(sys.path, fl, indent='\t')

def iterator__over_modules_into_pathes() -> pkgutil.ModuleInfo:
    with open('../production_2/pythonpath.json','r',encoding='utf-8') as fl:
        pathes = json.load( fl)
    for mod in pkg.iter_modules(pathes):
        yield mod












def save():
    mods = []
    for mod in pkg.iter_modules():
        mod_name = mod.name
        if mod_name.startswith('_'):
            print('module excepted...')
            continue
        mods.append(mod_name)

    csv_cont = ''
    for idx, mod in enumerate( mods):
        csv_cont += mod + ';'
        if idx % 6 == 0:
            csv_cont += '\n'

    with open('../production_2/all_modules.csv','w',encoding='utf-8') as fl:
        fl.write(csv_cont)

def get_mods():
    cont = ''
    with open('../production_2/all_modules.csv','r',encoding='utf-8') as fl:
        cont = fl.read()
    for line in cont.split('\n'):
        for module in line.split(';'):
            if module is None or module == '':
                continue
            yield module


if __name__ == '__main__':
    save_python_path()