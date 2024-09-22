import json
import re
import sys
from typing import Tuple

from treelib import Tree, Node

from seria_attribute import *


class SeriaTree:
    def __init__(self, path: str):
        self.file = open(path, 'r', encoding='cp1252')

        self.tree = Tree()

        self.depth = 0
        self.max_depth = 10

        self.classname = None
        self.parent_ids = []
        self.previous_line = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        self.file.close()

    def build(self, attribute_filter: dict = None, limit_depth=False):
        seria_input = self.file.readlines()

        for line_index in range(len(seria_input)):
            line = seria_input[line_index]

            if line.startswith('{'):
                self.depth += 1
            elif line.startswith('}'):
                if limit_depth:
                    if self.depth <= self.max_depth:
                        self.parent_ids.pop()
                else:
                    self.parent_ids.pop()

                self.depth -= 1
            else:
                attribute_name, attribute_value = matchAttribute(line)

                # data that follow the attribute-value pair format
                if attribute_name is not None:
                    # a node always start with m_classname
                    if attribute_name == 'm_classname':
                        if limit_depth and self.depth > self.max_depth:
                            continue

                        self.classname = attribute_value

                        # To avoid confusion, custom attribute name are Capitalized
                        initial_data = {
                            'Header': self.previous_line, 'LineIndex': line_index - 1}

                        if (len(self.parent_ids) > 0):
                            node = self.tree.create_node(
                                self.classname, parent=self.parent_ids[-1], data=initial_data)
                        else:
                            node = self.tree.create_node(
                                self.classname, data=initial_data)

                        self.parent_ids.append(node.identifier)
                    else:
                        node = self.tree.get_node(self.parent_ids[-1])

                        classname = node.tag
                        if attribute_filter is not None and classname in attribute_filter and attribute_name in attribute_filter[classname]:
                            if attribute_name in node.data:
                                if isinstance(node.data[attribute_name], list):
                                    node.data[attribute_name].append(
                                        attribute_value)
                                else:
                                    # make a list for multiple values
                                    node.data[attribute_name] = [
                                        node.data[attribute_name], attribute_value]
                            else:
                                node.data[attribute_name] = attribute_value

                            # e.g. m_escadras=327 is part of an Escadra node, but before the bracket
                    self.previous_line = line.strip()
                # other data, e.g. mesh data which has no attribute name
                else:
                    pass  # TODO

    def show(self) -> str:
        return self.tree.show(sorting=False, stdout=False)


def matchAttribute(input: str) -> Tuple[str, str]:
    match_object = re.match(ATTRIBUTE_PATTERN + '=' +
                            VALUE_PATTERN, input)

    if match_object:
        return match_object.group(1), match_object.group(2)

    return None, None


def readAttributeFilter(path: str) -> dict:
    attribute_config = json.load(open(path))
    attribute_filter = dict()

    for config in attribute_config:
        if 'NodeName' not in config or 'AttributeInclude' not in config:
            return None

        attribute_filter[config['NodeName']] = config['AttributeInclude']

    return attribute_filter


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python seria_tree.py <seria_file>')
        sys.exit(1)

    with SeriaTree(sys.argv[1]) as seria_tree:
        seria_tree.max_depth = 2
        seria_tree.build(limit_depth=True)
        print(seria_tree.show())
