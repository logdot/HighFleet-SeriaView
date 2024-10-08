import logging
import logging.config
from typing import List, Set
import re
from treelib import Node, Tree

ATTRIBUTE_PATTERN = r'([a-zA-Z][0-9a-zA-Z.:_]*)'
VALUE_PATTERN = r'(.*)'


def load(filepath: str, max_depth: int = None):
    logging.basicConfig(level=logging.DEBUG)

    file = open(filepath, 'r', encoding='cp1251')

    if file is None:
        logging.error('Could not open file: ' + filepath)
        return

    input_lines = file.readlines()
    tree = SeriaTree()
    depth = 0
    classname = None
    parent_ids = list()
    previous_line = None

    for line_index in range(len(input_lines)):
        line = input_lines[line_index]

        if line.startswith('{'):
            depth += 1
        elif line.startswith('}'):
            if max_depth is None or depth <= max_depth:
                parent_ids.pop()

            depth -= 1
        else:
            if max_depth and depth > max_depth:
                continue

            next_line_index = line_index + 1
            if next_line_index < len(input_lines):
                next_line = input_lines[line_index + 1]
                # the line before the '{' is belong to the upcomming node, will not add to the current node
                # e.g. m_escadras=327 is part of an Escadra node, but before the bracket
                if next_line.startswith('{'):
                    previous_line = line
                    continue

            attribute_name, attribute_value = _matchAttribute(line)

            if attribute_name is None:
                # TODO handle pure value lines (e.g. mesh data)
                if classname == 'Mesh':
                    node = tree.get_node(parent_ids[-1])
                    if '_meshData' in node.data:
                        node.data['_meshData'].append(line.strip())
                    else:
                        node.data['_meshData'] = [line.strip()]
            else:
                # e.g. m_schedule may have empty value, can be ignored
                if attribute_value == '':
                    continue
                # a node always start with m_classname
                if attribute_name == 'm_classname':
                    initial_data = {
                        '_header': None if previous_line is None else previous_line.strip()}

                    classname = attribute_value
                    if len(parent_ids) > 0:
                        node = tree.create_node(
                            classname, parent=parent_ids[-1], data=initial_data)
                    else:
                        node = tree.create_node(classname, data=initial_data)

                    parent_ids.append(node.identifier)
                else:
                    node = tree.get_node(parent_ids[-1])

                    if attribute_name not in node.data:
                        node.data[attribute_name] = attribute_value
                    elif isinstance(node.data[attribute_name], list):
                        node.data[attribute_name].append(attribute_value)
                    else:
                        # make a list for multiple values
                        node.data[attribute_name] = [
                            node.data[attribute_name], attribute_value]
    file.close()
    return tree


class SeriaNode(Node):
    def __init__(self, tag=None, identifier=None, expanded=True, data=None):
        super().__init__(tag, identifier, expanded, data)

    def get_attribute(self, attribute_name):
        '''Get the value of an attribute. Return None if the attribute not exist.'''
        if attribute_name in self.data:
            return self.data[attribute_name]
        return None

    def set_attribute(self, attribute_name, value):
        '''Set the value of an attribute. If the attribute not exist, it will be created.'''
        self.data[attribute_name] = value

    def remove_attribute(self, attribute_name):
        '''Remove an attribute. Return the value of the attribute if it exists.'''
        return self.data.pop(attribute_name, None)

    def get_attribute_names(self):
        return list(self.data.keys())


class SeriaTree(Tree):
    def __init__(self, tree=None, deep=False, node_class=SeriaNode, identifier=None):
        super().__init__(tree, deep, node_class, identifier)

    def to_text(self) -> str:
        '''Text representation of the tree structure.'''
        return self.show(stdout=False, sorting=False)

    def to_json(self) -> str:
        return super().to_json(with_data=True, sort=False)

    def child_node_types(self) -> Set[str]:
        '''Get all direct child node types of the root node.'''
        return set([child.tag for child in self.children(self.root)])

    def get_child_nodes(self, type: str = None) -> List[SeriaNode]:
        '''Get all direct child nodes of the root node with the specified type.'''
        if type is None:
            return self.children(self.root)
        return [child for child in self.children(self.root) if child.tag == type]

    def root_node(self) -> SeriaNode:
        return self.get_node(self.root)

    def add_child_node(self, node: SeriaNode):
        self.add_node(node, self.root_node())

    def remove_child_nodes_by_type(self, type: str):
        nodes = self.get_child_nodes(type)
        for node in nodes:
            self.remove_node(node.identifier)


def _matchAttribute(input: str):
    match_result = re.match(ATTRIBUTE_PATTERN + '=' + VALUE_PATTERN, input)

    if match_result:
        return match_result.group(1), match_result.group(2)

    return None, None
