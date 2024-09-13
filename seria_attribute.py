import re
import sys


class AttributeReader:
    def __init__(self, path):
        self.file = open(path, 'r', encoding='cp1252')

    def __enter__(self):
        return self

    def __exit__(self):
        self.file.close()

    def listAllAttributeName(self):
        matching = matchPattern(self.file, r'[a-zA-Z][0-9a-zA-Z.:_]*=')

        name_set = set()
        for match_object in matching:
            # -1 to remove '='
            name_set.add(match_object.group()[:-1])

        return sorted(name_set)

    def listAttributeValues(self, attribute_name):
        # make content after '=' to be a match group
        matching = matchPattern(self.file, attribute_name + r'=(.*)')

        value_set = set()
        for match_object in matching:
            value_set.add(match_object.group(1))

        return sorted(value_set)


def matchPattern(input, pattern):
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
