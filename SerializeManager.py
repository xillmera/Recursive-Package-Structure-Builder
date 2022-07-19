import pathlib
import json
import pickle

class SerializeManager:
    def __init__(self, prepath: str= '',
                 scheme_name : str=None,
                 st_obj_name:str='',
                 queue : dict =None):
        '''scheme должно находиться в prepath'''
        if prepath == '':
            prepath = 'SerializeManager'
        self.prepath = pathlib.Path(prepath)
        if not self.prepath.exists():
            self.prepath.mkdir()
        try:
            scheme = self.prepath / scheme_name
        except TypeError:
            scheme = self.prepath / 'scheme.json'
            if not scheme.exists():
                data = '{}'
                if st_obj_name:
                    data = json.dumps({st_obj_name:{'status':'queue'}})
                scheme.write_text(data)
        ''' num_obj = name in prepath
        obj_name:{
            'status': done | queue,
            'references':[obj_name_1, obj_name_2, obj_name_3]
        }
        '''
        self.scheme_path = scheme
        self.scheme = None
        self.refresh_scheme(reset_data=queue)

        pass

    def refresh_scheme(self, reset_data=None):
        '''если добавлять нечего просто перезагружает из схемы'''
        if reset_data :
            self.scheme = reset_data
        if self.scheme:
            for name in self.scheme.keys():
                try:
                    self.scheme[name]['references'] = list(self.scheme[name]['references'])
                except KeyError:
                    continue

            self.scheme_path.write_text(json.dumps(self.scheme, indent='\t'),'utf-8')
        tmp = json.loads(self.scheme_path.read_text('utf-8'))
        for name in tmp.keys():
            try:
                tmp[name]['references'] = set(tmp[name]['references'])
            except KeyError:
                continue
        self.scheme = tmp

    def check_exist_elem(self, target_obj_name):
        if not target_obj_name in self.scheme.keys():
            return False
        return True

    def check_done_elem(self, target_obj_name):
        try:
            if self.scheme[target_obj_name]['status']  == 'done':
                return True
        except KeyError:
            return False
        return False

    def deserialize_elem(self, target_obj_name):
        if not target_obj_name in self.scheme.keys():
            raise KeyError('such item not exist')
        tmp = None
        with (self.prepath / f'{target_obj_name}.ser').open(
                    'rb',
                    #encoding='utf-8'
                ) as fl:
            tmp = pickle.load(fl)
        return tmp

    def gen__scheme_item_data(self):
        for key in self.scheme:
            try:
                yield key, list(self.scheme[key]['references'])
            except KeyError:
                print(f'broken key {key}')
                continue


    def serialize_elem(self,
                       target_obj_name,
                       target_obj=None,
                       parent_obj_name=None,
                       f__miss_queue=False):

        try:
            status = self.scheme[target_obj_name]['status']
            if not status:
                raise NotImplementedError
        except (KeyError, NotImplementedError):
            status = 'queue'
            if f__miss_queue:
                status = 'except'

        if target_obj and status == 'queue':
            try:
                with (self.prepath / f'{target_obj_name}.ser')\
                        .open('wb') as fl:
                    pickle.dump(target_obj, fl)
                    status = 'done'
            except pickle.PicklingError:
                status = 'error'


        while True:
            try:
                self.scheme[target_obj_name]['status'] = status
                self.scheme[target_obj_name]['references'].add(parent_obj_name)
                break
            except KeyError:
                self.scheme[target_obj_name] = {
                    'status': None,
                    'references': set()
                }


    @property
    def queue(self):
        '''usefull'''
        return [
            name for name in self.scheme.keys()
            if not 'status' in self.scheme[name].keys()
            or self.scheme[name]['status'] == 'queue'
        ]

class SerializeManager__test:
    def __init__(self):
        self.obj = SerializeManager()

    def v1 (self):
        self.obj


if __name__ == '__main__':
    test = SerializeManager__test()
    test.v1()