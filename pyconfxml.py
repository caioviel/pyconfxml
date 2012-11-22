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
        
        #Iterate by the root elems
        childs = root.iterchildren()
        for elem in childs:
            if type (elem) != etree._Element:
                #just a comment
                continue
            
            
            if elem.tag == 'list':
                #It's a list
                self.parse_list(self.__config, elem)
                
            elif len(elem) == 0 and len(elem.items()) == 0:
                #It's an attribute
                self.parse_attribute(self.__config, elem)
            else:
                #It's an subnode
                self.parse_node(self.__config, elem)
                
            
        return self.__config
    
    def parse_list(self, parent_node, list_elem):
        pass
    
    def parse_attribute(self, parent_node, attribute_elem):
        attr_name = attribute_elem.tag
        attr_value = attribute_elem.text
        attr_value = self.__validator.check_and_convert_attribute(parent_node.tag, attr_name, attr_value)
        parent_node.set_attribute(attr_name, attr_value)
    
    def parse_node(self, parent_node, node_elem):
        node_id = node_elem.get('id')
        node_tag = node_elem.tag
        self.__validator.check_node(parent_node.tag, node_tag)
        
        if node_id == None:
            node_id = self.generate_id()
            
        node = CofigNode(node_id, node_elem.tag)
        
        childs = node_elem.iterchildren()
        unique_names_list = []
        for elem in childs:
            if type (elem) != etree._Element:
                #just a comment
                continue
            
            if elem.tag == 'list':
                #It's a list
                self.parse_list(self.__config, elem)
                
            elif len(elem) == 0 and len(elem.items()) == 0:
                #It's an attribute
                self.parse_attribute(node, elem)
            else:
                #It's an subnode
                self.parse_node(node, elem)
                
                
        self.__validator.check_required_attributes(node_tag, node.get_attributes_names())
        self.__validator.check_required_nodes(node_tag, node.get_child_nodes_tags())
        parent_node.add_node(node)
        
        
            
    def generate_id(self):
        import uuid
        return str(uuid.uuid4())
            
            
    
class ConfigValidator:
    def __init__(self, descriptor_file):
        pass
    
    def check_node(self, parent_tag, children_tag):
        pass
    
    def has_list(self, node_tag, list_name):
        pass
    
    def check_list_element(self, node_tag, list_name, tag_name):
        pass
    
    def check_and_convert_attribute(self, node_tag, attr_name, attr_value_str):
        return attr_value_str
    
    def check_required_attributes(self, node_tag, attr_names_list):
        pass
    
    def check_required_nodes(self, node_tag, node_tags_list):
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
        self.__children_nodes[node.id] = node
        self.__all_nodes[node.id] = node
        setattr(self, node.tag, node)
    
    def get_node(self, node_id):
        return self.__all_nodes[node_id]
    
    def add_list(self, list_name, mlist):
            setattr(object, 'list_' + list_name, mlist)
            self.__lists[list_name] = mlist
        
    def add_to_list(self, list_name, elem):
        if not self.__lists.has_key(list_name):
            new_list = []
            setattr(object, 'list_' + list_name, new_list)
            self.__lists[list_name] = new_list
        self.__lists[list_name].append(elem)
    
    def get_list(self, list_name):
        if not self.__lists.has_key(list_name):
            raise Exception("There is no list called " + list_name)
    
        return self.__lists[list_name]
    
    def set_attribute(self, attr_name, attr_value):
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

    

if __name__ == "__main__":
    test()
    
    
    
    
    