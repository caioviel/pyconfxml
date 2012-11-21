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
    def __init__(self, config=""):
        pass
    
class ConfigValidator:
    def check_node(self, parent_tag, children_tag):
        return True
    
    def has_list(self, node_tag, list_name):
        return True
    
    def check_list_element(self, node_tag, list_name, tag_name):
        return True
    
    def check_and_convert_attribute(self, node_tag, attr_name, attr_value_str):
        return True
    
    def check_required_attributes(self, node_tag, attr_names_list):
        return True
    
    def check_required_nodes(self, node_tag, node_tags_list):
        return True
        
class PyConfig:
    def add_node(self, node):
        pass
    
    def get_node(self, node_id):
        pass
    
    
class CofigNode:
    def __init__(self, tag, node_id):
        self.tag = tag
        self.node_id= node_id
        self.__nodes = {}
        self.__lists = {}
        self.__attributes_list = []
    
    def add_node(self, node):
        pass
    
    def get_node(self, node_id):
        pass
    
    def add_list(self, list_name, mlist):
        pass
        
    def add_to_list(self, list_name, elem):
        if not self.__lists.has_key(list_name):
            new_list = []
            setattr(object, 'list_' + list_name, new_list)
            self.__lists[list_name] = []
        self.__lists[list_name].append(elem)
    
    def get_list(self, list_name):
        if not self.__lists.has_key(list_name):
            raise Exception("There is no list called " + list_name)
    
        return self.__lists[list_name]
    
    def set_attribute(self, attr_name, attr_value):
        setattr(self, attr_name, attr_value)
    
    def get_attribute(self, attr_name):
        return getattr(self, attr_name)
            
    def has_attribute(self, attr_name):
        try:
            getattr(self, attr_name)
            return True
        except AttributeError:
            return False
        
    
def test():
    c = CofigNode('tag')
    setattr(c, 'teste', 5)
    print type(getattr(c, 'teste'))
    

if __name__ == "__main__":
    test()
    
    
    
    
    