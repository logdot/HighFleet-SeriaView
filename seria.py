import logging
import logging.config
import re
from treelib import Node, Tree

ATTRIBUTE_PATTERN = r'([a-zA-Z][0-9a-zA-Z.:_]*)'
VALUE_PATTERN = r'(.*)'


class SeriaNode(Node):
    def __init__(self, tag=None, identifier=None, expanded=True, data=None):
        super().__init__(tag, identifier, expanded, data)

    def has_attribute(self, attribute_name):
        return attribute_name in self.data

    def get_attribute(self, attribute_name):
        '''Get the value of an attribute. Return None if the attribute not exist.'''
        return self.data[attribute_name] if attribute_name in self.data else None

    def set_attribute(self, attribute_name, value):
        '''Set the value of an attribute. If the attribute not exist, it will be created.'''
        self.data[attribute_name] = value

    def del_attribute(self, attribute_name):
        '''Remove an attribute. Return the value of the attribute if it exists.'''
        return self.data.pop(attribute_name, None)

    def get_attribute_names(self):
        return list(self.data.keys())


class SeriaTree(Tree):
    def __init__(self, tree=None, deep=False, node_class=SeriaNode, identifier=None):
        super().__init__(tree, deep, node_class, identifier)

    def _root_node(self) -> SeriaNode:
        return self.get_node(self.root)

    def to_json(self) -> str:
        return super().to_json(with_data=True, sort=False)

    def to_text(self) -> str:
        '''Text representation of the tree structure.'''
        return self.show(stdout=False, sorting=False)

    def clone(self):
        '''Create a deep copy of the tree.'''
        return super()._clone(with_tree=True, deep=True)

    # root node operation
    def get_attribute(self, attribute_name):
        '''Get the attribute value of the root node. Return None if the attribute not exist.'''
        root_node = self._root_node()
        return root_node.data[attribute_name] if attribute_name in root_node.data else None

    def set_attribute(self, attribute_name, value):
        '''Set the attribute value of the root node. If the attribute not exist, it will be created.'''
        self._root_node().data[attribute_name] = value

    def del_attribute(self, attribute_name):
        '''Remove an attribute from the root node. Return the value of the attribute if it exists.'''
        return self._root_node().data.pop(attribute_name, None)

    def get_attribute_names(self):
        return list(self._root_node().data.keys())

    # child node operation
    def get_node_by_index(self, index: int) -> SeriaNode:
        '''Get a child node by its order(index) in the file.'''
        return self.get_nodes()[index]

    def get_node_if(self, predicate) -> SeriaNode:
        '''Get the first child node that satisfy the predicate function.'''

        for child in self.children(self.root):
            if predicate(child):
                return child
        return None

    def get_node_by_class(self, type: str) -> SeriaNode:
        '''Get the first child node with the specified classname.'''
        return self.get_node_if(lambda node: node.tag == type)

    # child nodes read operation
    def get_nodes(self) -> list:
        '''Get all direct child nodes of the root node.'''
        return self.children(self.root)

    def get_nodes_by_class(self, type: str) -> filter:
        '''Get all direct child nodes of the root node with the specified type.'''
        return self.filter_nodes(lambda node: node.tag == type)

    def map_nodes(self, mapper) -> list:
        '''Returns a result list of applying the mapper function to all child nodes.'''
        return [mapper(child) for child in self.children(self.root)]

    def node_classes(self) -> set:
        '''Get all direct child node types of the root node.'''
        return set(self.map_nodes(lambda node: node.tag))

    # child nodes write operation
    def add_nodes(self, nodes: list):
        for node in nodes:
            self.add_node(node, self._root_node())

    def del_node_by_index(self, index: int):
        '''Remove a child node by its order(index) in the file.'''
        nodes = self.get_nodes()
        self.remove_node(nodes[index].identifier)

    def del_nodes(self, nodes: list) -> int:
        '''Remove all child nodes in the list. Return the number of nodes removed.'''

        count = 0
        for node in nodes:
            count += self.remove_node(node)
        return count

    def del_nodes_if(self, predicate) -> int:
        '''Remove all child nodes that satisfy the predicate (condition) function. Return the number of nodes removed.'''

        nodes = [child for child in self.children(
            self.root) if predicate(child)]
        return self.del_nodes(nodes)

    def del_nodes_by_class(self, classname: str) -> int:
        '''Remove all child nodes with the specified classname. Return the number of nodes removed.'''
        return self.del_nodes_if(lambda node: node.tag == classname)

    def foreach_node(self, action):
        '''Apply the action function to all child nodes.'''
        for child in self.children(self.root):
            action(child)

    # child tree operation
    def get_subtree_by_index(self, index: int):
        '''Get a subtree (shallow) by its order(index) in the file.'''
        return self.subtree(self.get_node_by_index(index).identifier)

    def get_subtree_if(self, predicate):
        '''Get the first subtree that satisfy the predicate function.'''

        for child in self.children(self.root):
            if predicate(child):
                return self.subtree(child.identifier)
        return None


def _matchAttribute(input: str):
    '''Match an attribute and its value from a line of text. Return a tuple of the attribute and its value.'''

    match_result = re.match(ATTRIBUTE_PATTERN + '=' + VALUE_PATTERN, input)
    if match_result:
        return match_result.group(1), match_result.group(2)
    return None, None


def dump(tree: SeriaTree) -> str:
    '''Dump the tree back to the seria format.'''

    root = tree._root_node()

    output = []
    header = root.data['_header']
    if header:
        output.append(header)

    output.append('{')

    for key, value in root.data.items():
        if key == '_header':
            continue
        elif key == '_meshData':
            for item in value:
                output.append(item)
        elif isinstance(value, list):
            for item in value:
                output.append(f'{key}={item}')
        else:
            output.append(f'{key}={value}')

    for child in tree.children(root.identifier):
        output.append(dump(tree.subtree(child.identifier)))

    output.append('}')

    return '\n'.join(output)


def load(filepath: str, max_depth: int = None) -> SeriaTree:
    '''Load a seria file and return a tree structure.
    load function uses original treelib functions to create and manage the tree structure.
    Beaware that SeriaTree is a subclass of Tree, and may have overidden methods.
    @param filepath: The path to the seria file.
    @param max_depth: The maximum depth of the tree. If None, the tree will be fully parsed.
    @return: The tree structure or None if the file could not be opened.'''

    logging.basicConfig(level=logging.DEBUG)

    try:
        with open(filepath, 'r', encoding='cp1251') as file:
            input_lines = file.readlines()
    except IOError:
        logging.error(f'Could not open file: {filepath}')
        return None

    tree = SeriaTree()
    depth = 0
    classname = None
    parent_ids = []
    previous_line = None

    for line_index, line in enumerate(input_lines):
        line = line.strip()

        if line == '{':
            depth += 1
        elif line == '}':
            if max_depth is None or depth <= max_depth:
                parent_ids.pop()
            depth -= 1
        else:
            if max_depth and depth > max_depth:
                continue

            next_line_index = line_index + 1
            if next_line_index < len(input_lines):
                # the line before the curly brace is belong the next node
                # e.g. 'm_escadras=327' is belong to node 'Escadra'
                next_line = input_lines[next_line_index].strip()
                if next_line == '{':
                    previous_line = line
                    continue

            attribute_name, attribute_value = _matchAttribute(line)

            if attribute_name is None:
                # handle the case where the line is a value with no attribute name
                if classname == 'Mesh':
                    node = tree.get_node(parent_ids[-1])
                    node.data.setdefault('_meshData', []).append(line)
            else:
                # it is safe to skip empty attribute values
                if attribute_value == '':
                    continue

                if attribute_name == 'm_classname':
                    # create a new node, always starts with m_classname
                    classname = attribute_value
                    initial_data = {'_header': previous_line.strip() if previous_line else None,
                                    'm_classname': classname}
                    node = tree.create_node(
                        classname, parent=parent_ids[-1] if parent_ids else None, data=initial_data)
                    parent_ids.append(node.identifier)
                else:
                    node = tree.get_node(parent_ids[-1])
                    if attribute_name in node.data:
                        if isinstance(node.data[attribute_name], list):
                            node.data[attribute_name].append(attribute_value)
                        else:
                            node.data[attribute_name] = [
                                node.data[attribute_name], attribute_value]
                    else:
                        node.data[attribute_name] = attribute_value

    return tree
