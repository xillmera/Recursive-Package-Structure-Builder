'''
Программа для подготовки объектов в YeD редакторе
на вход поступает последовательность строк 
каждая из которых попадает в отдельный объект диаграммы
если встречается #t то объекты перестают идти в одном столбце и начинают в новом
'''
import pathlib 

class Graph_XML_builder:
    st__Graph_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:java="http://www.yworks.com/xml/yfiles-common/1.0/java" xmlns:sys="http://www.yworks.com/xml/yfiles-common/markup/primitives/2.0" xmlns:x="http://www.yworks.com/xml/yfiles-common/markup/2.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:y="http://www.yworks.com/xml/graphml" xmlns:yed="http://www.yworks.com/xml/yed/3" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd">
  <!--Created by yEd 3.21.1-->
  <key attr.name="Description" attr.type="string" for="graph" id="d0"/>
  <key for="port" id="d1" yfiles.type="portgraphics"/>
  <key for="port" id="d2" yfiles.type="portgeometry"/>
  <key for="port" id="d3" yfiles.type="portuserdata"/>
  <key attr.name="url" attr.type="string" for="node" id="d4"/>
  <key attr.name="description" attr.type="string" for="node" id="d5"/>
  <key for="node" id="d6" yfiles.type="nodegraphics"/>
  <key for="graphml" id="d7" yfiles.type="resources"/>
  <key attr.name="url" attr.type="string" for="edge" id="d8"/>
  <key attr.name="description" attr.type="string" for="edge" id="d9"/>
  <key for="edge" id="d10" yfiles.type="edgegraphics"/>
  <graph edgedefault="directed" id="G">
    <data key="d0"/>
  '''
    ed__Graph_xml = '''  </graph>
  <data key="d7">
    <y:Resources/>
  </data>
</graphml>
'''
    class Content(list):
        def __str__(self):
            res = ''
            for item in self:
                res+=item['xml']
            return res

        def add_node(self, xml, text, nodeID ):
            self.append({
                    'type':'node',
                    'xml':xml,
                    'text':text,
                    'nodeID':nodeID
                })


        def add_edge(self, xml, nodeID__source, nodeID__target ):
            self.append({
                    'type':'edge',
                    'xml':xml,
                    'nodeID':{
                        'source':nodeID__source,
                        'target':nodeID__target
                    }
                })

        def check_edge_exists(self, nodeID__source, nodeID__target ):
            for item in self:
                if item['type'] != 'edge':
                    continue
                tmp = [
                    item['nodeID']['source'] == nodeID__source,
                    item['nodeID']['target'] == nodeID__target
                ]
                if all(tmp):
                    return True
            return False

        def get_node_id(self, text):
            for item in self:
                if not item['type'] == 'node':
                    continue
                if item['text'] == text:
                    return item['nodeID']
            return None

    def clear(self):
        self.content = self.Content()
        self.counter = -1
        self.x_pos = 0
        self.y_pos = 0
        self.sep_counter = -1
        self.edge_counter = -1
        self.unique_names = set()

    def __init__ (self, high = 30, width = 100, sep_limit_h = 15, f__no_limit=True ):
        self.clear()
        self.high = high
        self.width = width

        self.shift_width = width*2
        self.sep_limit_h = sep_limit_h
        if f__no_limit:
            self.sep_limit_h = float('Infinity')
        self.high_sep = int( self.high / 5 )

    def translate(self, input_text:str ):
        '''full graph xml
        by nodes
        from predefined template
        from txt file'''
        label_detected = False
        for line in input_text.split('\n'):
            if '#t' in line:
                label_detected = True
                continue
            tmp = line.strip()
            self.node_insert(tmp, label_detected)
            label_detected = False

    def create_edge_from_two_text_if_exist(self,text1,text2, f__unique_vals = False, **kwargs):
        '''если одной из нод не существует поднимает ошибку ValueError
        text1 -> text2
        если установлен флаг f__unique_vals = True то вызывает ошибку ValueError
        '''
        nodeID_1v = self.content.get_node_id(text1)
        nodeID_2v = self.content.get_node_id(text2)
        if f__unique_vals:
            if self.content.check_edge_exists(nodeID_1v, nodeID_2v):
                raise ValueError

        if nodeID_1v and nodeID_2v:
            self.edge_insert(nodeID_1v, nodeID_2v, **kwargs)
            return
        raise ValueError

    def edge_insert (self, nodeID__source, nodeID__target, points_xy_list=None, width = 1.0):
        self.edge_counter += 1
        data_keys = "<data key='d9'/>\n" + '  '*3 + '<data key="d10">'
        point_path = '<y:Path sx="0.0" sy="0.0" tx="0.0" ty="0.0"/>'
        if points_xy_list:
            data_keys =  '<data key="d10">'

            point_path = '<y:Path sx="0.0" sy="0.0" tx="0.0" ty="0.0">'
            point_path += '\n'+'\n'.join([
                    '  '*6+f'<y:Point x="{x}" y="{y}"/>'
                    for x,y in points_xy_list
                ])
            point_path += '  '*5+'</y:Path>'
        tmp_edge_text = f'''  <edge id="e{self.edge_counter}" source="{nodeID__source}" target="{nodeID__target}">
      {data_keys}
        <y:PolyLineEdge>
          {point_path}
          <y:LineStyle color="#000000" type="line" width="{width}"/>
          <y:Arrows source="none" target="standard"/>
          <y:BendStyle smoothed="false"/>
        </y:PolyLineEdge>
      </data>
    </edge>
  '''
        self.content.add_edge(xml=tmp_edge_text,
                              nodeID__source=nodeID__source,
                              nodeID__target=nodeID__target)

    def col_shift(self, prep_shift=None, f__y_return=True):
        x_shift = self.shift_width
        if prep_shift:
            x_shift = int(prep_shift)
        self.x_pos += x_shift
        if f__y_return:
            self.sep_counter = -1

    def node_insert (self,
                     text,
                     force_break = False,
                     prep_shift=None,
                     color = 'FFCC00',
                     fontsize = 12,
                     f__unique_names = False) -> tuple:
        '''возвращает координаты установки ноды и её параметры
         в следующем порядке: x, y, high, width
         '''
        if f__unique_names :
            if text in self.unique_names:
                raise ValueError
            else:
                self.unique_names.add(text)

        auto_width = int(self.width/14*len(text)) + 10

        if self.sep_counter > self.sep_limit_h or force_break:
            self.col_shift(prep_shift=prep_shift if prep_shift else auto_width)
        self.counter += 1
        self.sep_counter += 1
        self.y_pos = (self.high+self.high_sep)*self.sep_counter

        tmp_node_text = f'''  <node id="n{self.counter}">
      <data key="d5"/>
      <data key="d6">
        <y:ShapeNode>
          <y:Geometry height="{self.high}.0" width="{auto_width}.0" x="{self.x_pos}.0" y="{self.y_pos}"/>
          <y:Fill color="#{color}" transparent="false"/>
          <y:BorderStyle color="#000000" raised="false" type="line" width="1.0"/>
          <y:NodeLabel alignment="center" autoSizePolicy="content" fontFamily="Dialog" fontSize="{fontsize}" fontStyle="plain" hasBackgroundColor="false" hasLineColor="false" height="{str(fontsize*12/18.701171875)}" horizontalTextPosition="center" iconTextGap="4" modelName="custom" textColor="#000000" verticalTextPosition="bottom" visible="true" width="56.01953125" x="16.490234375" xml:space="preserve" y="5.6494140625">{text}<y:LabelModel><y:SmartNodeLabelModel distance="4.0"/></y:LabelModel><y:ModelParameter><y:SmartNodeLabelModelParameter labelRatioX="0.0" labelRatioY="0.0" nodeRatioX="0.0" nodeRatioY="0.0" offsetX="0.0" offsetY="0.0" upX="0.0" upY="-1.0"/></y:ModelParameter></y:NodeLabel>
          <y:Shape type="rectangle"/>
        </y:ShapeNode>
      </data>
    </node>
  '''
        self.content.add_node(xml=tmp_node_text,
                              text=text,
                              nodeID=f'n{self.counter}')
        return self.x_pos, self.y_pos, self.high, auto_width



    def get_XML(self):
        return self.st__Graph_xml + str(self.content) + self.ed__Graph_xml

if __name__ == '__main__':

    input_file = 'text.txt'
    target_file = 'target.graphml'

    p = pathlib.Path(input_file)
    if not p.exists():
        p.touch()
        input('Nothing to work')
        exit()

    gb = Graph_XML_builder()
    with p.open() as fl:
        label_detected = False
        for line in fl:
            if '#t' in line :
                label_detected = True
                continue
            tmp = line.strip()
            gb.node_insert(tmp, label_detected)
            label_detected = False

    t = pathlib.Path(target_file)
    with t.open( 'w', encoding='UTF-8') as fl:
        #print(gb.get_XML())
        #input('im here')
        tmp = gb.get_XML()
        fl.write(tmp)

    input('end of prog')

