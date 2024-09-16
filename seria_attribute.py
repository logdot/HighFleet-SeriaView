import re
import sys
from collections import Iterable

ATTRIBUTE_PATTERN = r'([a-zA-Z][0-9a-zA-Z.:_]*)'
VALUE_PATTERN = r'(.*)'


class AttributeReader:
    def __init__(self, path):
        self.file = open(path, 'r', encoding='cp1252')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()

    def listAllAttributeName(self) -> list:
        matching = matchPattern(
            self.file, ATTRIBUTE_PATTERN + '=' + VALUE_PATTERN)

        name_set = set()
        for match_object in matching:
            name_set.add(match_object.group(1))

        return sorted(name_set)

    def listAttributeValues(self, attribute_name: str) -> list:
        matching = matchPattern(
            self.file, attribute_name + '=' + VALUE_PATTERN)

        value_set = set()
        for match_object in matching:
            value_set.add(match_object.group(1))

        return sorted(value_set)


def matchPattern(input: Iterable, pattern: str) -> list:
    matching = list()

    for line in input:
        match_object = re.match(pattern, line)
        if match_object:
            matching.append(match_object)

    return matching


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python seria_attribute.py <seria_file>')
        sys.exit(1)

    with AttributeReader(sys.argv[1]) as reader:
        print('Attribute names:')
        for name in reader.listAllAttributeName():
            print(name)
