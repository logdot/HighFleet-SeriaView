import logging
import logging.config
import re

__author__ = 'Max'
__version__ = '0.1.0'

ATTRIBUTE_PATTERN = r'([a-zA-Z][0-9a-zA-Z.:_]*)'
VALUE_PATTERN = r'(.*)'

# logging.basicConfig(level=logging.DEBUG)


class alist:
    '''Association list that maintains the order of key-value pairs and allows insertion.
    The dict part is used to store the data, while the list part is used to store the order of insertion.'''

    def __init__(self, data: dict = None):
        self.data = data or dict()
        self.order = list(data.keys())

    def __iter__(self):
        for key in self.order:
            yield key, self.get(key)

    def __contains__(self, key) -> bool:
        return key in self.keys()

    # list operations
    def insert(self, index, key, value):
        self.data[key] = value
        self.order.insert(index, key)

    def remove(self, key):
        del self.data[key]
        self.order.remove(key)

    def index(self, key) -> int:
        return self.order.index(key)

    # dict operations
    def get(self, key):
        return self.data.get(key)

    def keys(self):
        return set(self.order)

    def put(self, key, value):
        self.data[key] = value
        if key not in self.order:
            self.order.append(key)


class SeriaNode:
    def __init__(self, header: str, classname: str):
        self.header = header
        self.data_group = list()
        self.data_group.append(alist({'m_classname': classname}))

    def _add_attribute(self, name: str, value: str):
        last_group = self.data_group[-1]
        if not isinstance(last_group, alist):
            self.data_group.append(alist({name: value}))
        else:
            if name in last_group:
                existing_value = last_group.get(name)
                if isinstance(existing_value, list):
                    last_group.put(name, existing_value + [value])
                else:
                    last_group.put(name, [existing_value, value])
            else:
                last_group.put(name, value)

    def _add_child(self, node):
        if not isinstance(node, SeriaNode):
            logging.error('Child must be a SeriaNode')
            return
        self.data_group.append(node)

    # node read operations
    def get_attribute(self, name: str):
        for group in self.data_group:
            if isinstance(group, alist):
                # assume that attribute only appear in consecutive order and will not spread accross groups
                if name in group.keys():
                    return group.get(name)
        return None


def _match_attribute(input: str):
    '''Match an attribute and its value from a line of text.
    @return: a tuple of the attribute and its value, or None if no match'''

    match_result = re.match(ATTRIBUTE_PATTERN + '=' + VALUE_PATTERN, input)
    if match_result:
        return match_result.group(1), match_result.group(2)
    return None, None


def _dump(node: SeriaNode) -> str:
    '''Dump a SeriaNode to a string.'''

    output = []

    if node.header is not None:
        output.append(node.header)
    output.append('{')

    for group in node.data_group:
        if isinstance(group, alist):
            for name, value in group:
                if name == '_mesh':
                    output.extend(f'{v}' for v in value)
                else:
                    if isinstance(value, list):
                        output.extend(f'{name}={v}' for v in value)
                    else:
                        output.append(f'{name}={value}')
        else:
            output.append(_dump(group))

    output.append('}')
    return '\n'.join(output)


def dump(filepath: str, node: SeriaNode):
    '''Dump a SeriaNode to a file.'''

    logger = logging.getLogger('seria.dump')

    try:
        with open(filepath, 'w', encoding='cp1251') as file:
            file.write(_dump(node) + '\n')
    except IOError:
        logger.error(f'Could not open file: {filepath}')


def load(filepath: str) -> SeriaNode:
    '''Load a SeriaNode from a file.
    @return: the root node of the SeriaNode, or None if the file could not be opened'''

    logger = logging.getLogger('seria.load')

    try:
        with open(filepath, 'r', encoding='cp1251') as file:
            lines = file.readlines()
    except IOError:
        logger.error(f'Could not open file: {filepath}')
        return None

    parent_nodes = list()
    header_line = None
    node = None

    for index, line in enumerate(lines):
        line = line.strip()

        if line == '{':
            continue
        elif line == '}':
            # the last '}' will give the last node which is the root node and return it at the end
            node = parent_nodes.pop()
        else:
            # the line before the curly brace is belong the next node
            # e.g. 'm_escadras=327' is belong to node 'Escadra'
            next_index = index + 1
            if next_index < len(lines):
                next_line = lines[next_index].strip()
                if next_line == '{':
                    header_line = line
                    continue

            name, value = _match_attribute(line)

            if name == 'm_classname':
                logger.info(f'new node: {value}')

                node = SeriaNode(header_line, value)

                if len(parent_nodes) > 0:
                    parent_nodes[-1]._add_child(node)

                parent_nodes.append(node)
            elif name is None:
                node = parent_nodes[-1]

                if node.data_group[0].get('m_classname') == 'Mesh':
                    node._add_attribute('_mesh', line)
            else:
                logger.debug(f'new attribute: {name} = {value}')

                parent_nodes[-1]._add_attribute(name, value)

    return node
