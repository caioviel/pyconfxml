'''
Created on Nov 21, 2012

@author: caioviel
'''

from lxml import etree

### Each node is mapped into a object (nested)
### Node without attributes or subnodes are attributes in the objects
#### Reserved nomes: reference list
################# must have attribute "id".

### Attributes are attributes in the objects
###### Reserved attributes: id
### You can have a list of objects mapped as array
### Configurations can be validated by a XML schema or by a configuration description 
### 

class PyConfigReader: 
    def __init__(self, descriptor_file=None, pythonic_names=False):
        self.descriptor_file = descriptor_file
        self.pythonic_names = pythonic_names
        self.__validator = ConfigValidator(self.descriptor_file)
    
    def get_configuration(self, filename):
        mfile = open(filename, 'r')
        tree = etree.parse(mfile)
        root = tree.getroot();
        if root.tag != 'configuration':
            raise Exception('Root elem must be <configuration>. Found <' + root.tag + '>')
            
        config_id = root.get('id')
        descriptor_file = root.get('configurationDescription')
        self.__config = PyConfig(config_id)
        self.__references_to_solve = []
        
        #Iterate by the root elems
        childs = root.iterchildren()
        for elem in childs:
            if type (elem) != etree._Element:
                #just a comment
                continue
            
            if elem.tag == 'list':
                #It's a list
                self.parse_list(self.__config, elem)
                
            elif elem.tag == 'reference':
                #It's a reference
                self.parse_reference(self.__config, elem)
                
            elif len(elem) == 0 and len(elem.items()) == 0:
                #It's an attribute
                attrname, attrvalue = self.parse_attribute(self.__config, elem)
                self.__config.set_attribute(attrname, attrvalue)
                
            else:
                #It's an subnode
                self.__config.add_node(  self.parse_node(self.__config, elem) )
                
        self.__validator.check_required_attributes('root', self.__config.get_attributes_names())
        self.__validator.check_required_nodes('root', self.__config.get_child_nodes_tags())
        
        for parent_node, refer_name, node_id, sourceline in self.__references_to_solve:
            referred_node = None
            try:
                referred_node = self.__config.get_node(node_id)
            except:
                raise Exception('Line %d: An invalid noneId "%s" referred.' % \
                                (sourceline, refer_name))
            
            self.__validator.check_reference(parent_node.tag, refer_name, referred_node.tag)
            parent_node.set_attribute(refer_name, referred_node)
            
        
        return self.__config
    
    def parse_list(self, parent_node, list_elem):
        list_name = list_elem.get('name')
        self.__validator.check_list(parent_node.tag, list_name)
        
        childs = list_elem.iterchildren()
        parent_node
        for elem in childs:
            if type (elem) != etree._Element:
                #just a comment
                continue
                
            if len(elem) == 0 and len(elem.items()) == 0:
                #It's just a primitive
                str_value = elem.text
                if str_value == None:
                    raise Exception("Line %d: A primitive list element must have a text." \
                                    % (elem.sourceline))
                
                list_value = self.__validator.check_and_convert_list_primitive(\
                                    parent_node.tag, list_name, elem.tag, elem.text)
                
                parent_node.add_to_list(list_name, list_value)
                
            else:
                #It's an subnode
                node = self.parse_node(self.__config, elem)
                self.__validator.check_list_node(parent_node.tag, list_name, node.tag)
                parent_node.add_node_to_list(list_name, node)
        
    
    def parse_reference(self, parent_node, refer_elem):
        refer_name = refer_elem.get('name')
        node_id = refer_elem.get('nodeId')
        if refer_name == None:
            raise Exception('Line %d: <reference> must have a attribute "name".' % refer_elem.sourceline)
        
        if node_id == None:
            raise Exception('Line %d: <reference> must have a attribute "nodeId".' % refer_elem.sourceline)
            
        self.__references_to_solve.append( (parent_node, refer_name, node_id, refer_elem.sourceline) )
    
    def parse_attribute(self, parent_node, attribute_elem):
        attr_name = attribute_elem.tag
        attr_value = attribute_elem.text
        attr_value = self.__validator.check_and_convert_attribute(parent_node.tag, attr_name, attr_value)
        return attr_name, attr_value
    
    def parse_node(self, parent_node, node_elem):
        node_id = node_elem.get('id')
        node_tag = node_elem.tag
        self.__validator.check_node(parent_node.tag, node_tag)
        
        if node_id == None:
            node_id = self.generate_id()
            
        node = CofigNode(node_id, node_elem.tag)
        
        for attr_name, attr_value in node_elem.items():
            if attr_name == 'id':
                continue
            
            attr_value = self.__validator.check_and_convert_attribute(\
                                    node.tag, attr_name, attr_value)            
            node.set_attribute(attr_name, attr_value)
        
        
        childs = node_elem.iterchildren()
        for elem in childs:
            if type (elem) != etree._Element:
                #just a comment
                continue
            
            if elem.tag == 'list':
                #It's a list
                self.parse_list(node, elem)
                
            elif elem.tag == 'reference':
                #It's a reference
                self.parse_reference(node, elem)
                
            elif len(elem) == 0 and len(elem.items()) == 0:
                #It's an attribute
                attr_name, attr_value = self.parse_attribute(node, elem)
                node.set_attribute(attr_name, attr_value)
                
            else:
                #It's an subnode
                node.add_node( self.parse_node(node, elem) )
                
                
        self.__validator.check_required_attributes(node_tag, node.get_attributes_names())
        self.__validator.check_required_nodes(node_tag, node.get_child_nodes_tags())
        return node
        
            
    def generate_id(self):
        import uuid
        return str(uuid.uuid4())
            
            
    
class ConfigValidator:
    def __init__(self, descriptor_file):
        pass
    
    def check_node(self, parent_tag, children_tag):
        pass
    
    def check_list(self, node_tag, list_name):
        pass
    
    def check_and_convert_list_primitive(self, node_tag, list_name, tag_name, value):
        return value
    
    def check_list_node(self, node_tag, list_name, tag_name):
        pass
    
    def check_and_convert_attribute(self, node_tag, attr_name, attr_value_str):
        return attr_value_str
    
    def check_required_attributes(self, node_tag, attr_names_list):
        pass
    
    def check_required_nodes(self, node_tag, node_tags_list):
        pass
    
    def check_reference(self, parent_node_tag, refer_name, refer_tag):
        pass
        
class PyConfig:
    __all_nodes = {}
    
    def __init__(self, node_id, tag='root'):
        self.tag = tag
        self.__all_nodes = {}
        self.__children_nodes = {}
        self.__lists = {}
        self.__attributes_list = []
        self.id = node_id
        
    def get_child_nodes(self):
        return self.__children_nodes.values()
        
    def get_child_nodes_tags(self):
        return [child.tag for child in self.__children_nodes.values()]
        
    def get_attributes_names(self):
        return self.__attributes_list
    
    
    def add_node(self, node):
        if self.has_attribute(node.tag):
            raise Exception('Trying to override the symbol "%s" inside a "%s"' \
                            % (node.tag, self.tag))
            
        self.__children_nodes[node.id] = node
        self.__all_nodes[node.id] = node
        setattr(self, node.tag, node)
    
    def get_node(self, node_id):
        return self.__all_nodes[node_id]
    
    def add_list(self, list_name, mlist):
        setattr(self, list_name, mlist)
        self.__lists[list_name] = mlist
        
    def add_to_list(self, list_name, elem):
        if not self.__lists.has_key(list_name):
            new_list = []
            setattr(self, list_name, new_list)
            self.__lists[list_name] = new_list
            
        self.__lists[list_name].append(elem)
        
    def add_node_to_list(self, list_name, node):
        if not self.__lists.has_key(list_name):
            new_list = []
            setattr(self, list_name, new_list)
            self.__lists[list_name] = new_list
        
        self.__lists[list_name].append(node)
        self.__all_nodes[node.id] = node
        
    
    def get_list(self, list_name):
        if not self.__lists.has_key(list_name):
            raise Exception("There is no list called " + list_name)
    
        return self.__lists[list_name]
    
    def set_attribute(self, attr_name, attr_value):
        if self.has_attribute(attr_name):
            raise Exception('Trying to override the symbol "%s" inside a "%s"' \
                            % (attr_name, self.tag))
        
        self.__attributes_list.append(attr_name)
        setattr(self, attr_name, attr_value)
    
    def get_attribute(self, attr_name):
        return getattr(self, attr_name)
            
    def has_attribute(self, attr_name):
        try:
            getattr(self, attr_name)
            return True
        except AttributeError:
            return False
    
    
class CofigNode(PyConfig):
    def __init__(self, node_id, tag):
        PyConfig.__init__(self, node_id, tag)
    
    def get_node(self, node_id):
        return self.__children_nodes[node_id]
        
    
def test():
    parser = PyConfigReader()
    config = parser.get_configuration('file.xml')
    print config.id
    print config.attrRoot1
    print config.attrRoot2
    print config.object1.name
    print config.object1.suboject1.name
    print config.object2.myReference.name
    print config.object1.minha_lista_de_coisas

    

if __name__ == "__main__":
    test()
    
    
    
    
    