import logging
import sys
import seria


def _print_help():
    print('''Usage: python seria.py [option] <seria_files...>
Options:
    -attributes              | List all distinct attributes
    -values <attribute name> | List all distinct values for the given attribute
    -tree                    | Print the tree representation with depth 3
    -json                    | Convert the given seria files to JSON
Example:
    python seria.py -values m_classname profile.seria parts.seria''')


def process_files_by_line(filepaths, process_line):
    '''Process files with the given line processing function'''

    for filepath in filepaths:
        try:
            with open(filepath, 'r', encoding='cp1251') as file:
                result_set = set()

                for line in file:
                    process_line(line, result_set)

                # allows the caller to iterate over the results
                yield filepath, result_set
        except IOError:
            logging.error('Could not open file: ' + filepath)


def process_files_by_tree(filepaths, process, depth=None):
    '''Process files with the given tree processing function'''

    for filepath in filepaths:
        try:
            tree = seria.load(filepath, depth)
            if tree is None:
                logging.error(f'Could not open file: {filepath}')
                continue

            yield filepath, process(tree)
        except IOError:
            logging.error(f'Could not process file: {filepath}')


def list_attributes(filepaths):
    '''List all distinct attributes in the given files'''

    def process_line(line, result_set):
        attribute, _ = seria._matchAttribute(line)
        if attribute is not None:
            result_set.add(attribute)

    for filepath, attribute_set in process_files_by_line(filepaths, process_line):
        print(f'Attributes in file {filepath}:')
        for attribute in sorted(attribute_set):
            print(attribute)


def list_values(attribute_name, filepaths):
    '''List all distinct values for the given attribute in the given files'''

    def process_line(line, result_set):
        attribute, value = seria._matchAttribute(line)
        if attribute == attribute_name:
            result_set.add(value)

    for filepath, value_set in process_files_by_line(filepaths, process_line):
        print(f'Values for attribute {attribute_name} in file {filepath}:')
        for value in sorted(value_set):
            print(value)


def print_seria_tree_file(filepaths):
    '''Print the tree representation of the given files with depth 3'''

    for filepath, output in process_files_by_tree(filepaths, lambda tree: tree.to_text(), 3):
        file = open(filepath + '.tree.txt', 'w')
        file.write(output)
        file.close()
        print(f'Tree representation for file {filepath} save to {file.name}')


def print_seria_json_file(filepaths):
    '''Convert the given seria files to JSON'''

    for filepath, output in process_files_by_tree(filepaths, lambda tree: tree.to_json()):
        file = open(filepath + '.json', 'w')
        file.write(output)
        file.close()
        print(f'JSON representation for file {filepath} save to {file.name}')


if __name__ == '__main__':
    argv_len = len(sys.argv)

    if argv_len < 3:
        _print_help()
        sys.exit(0)

    option = sys.argv[1]

    if option == '-attributes':
        list_attributes(sys.argv[2:])
    elif option == '-values':
        if argv_len < 4:
            logging.error('Missing attribute name')
            _print_help()
            sys.exit(1)

        list_values(sys.argv[2], sys.argv[3:])
    elif option == '-tree':
        print_seria_tree_file(sys.argv[2:])
    elif option == '-json':
        print_seria_json_file(sys.argv[2:])
    else:
        logging.error(f'Invalid option: {option}')
        _print_help()
        sys.exit(1)
