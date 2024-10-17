import logging
import sys
import seria

__author__ = 'Max'
__version__ = '0.3.0'


def _print_help():
    print('''Usage: python seria.py [option] <seria_files...>
Options:
    -attributes              | List all distinct attributes
    -values <attribute name> | List all distinct values for the given attribute
    -flagship                | Set the given ship design files to be a flagship
    -tree [<depth>]          | Print the tree structure of the seria file with optional depth
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


def list_attributes(filepaths):
    '''List all distinct attributes in the given files'''

    def process_line(line, result_set):
        attribute, _ = seria._match_attribute(line)
        if attribute is not None:
            result_set.add(attribute)

    for filepath, attribute_set in process_files_by_line(filepaths, process_line):
        print(f'Attributes in file {filepath}:')
        for attribute in sorted(attribute_set):
            print(attribute)


def list_values(attribute_name, filepaths):
    '''List all distinct values for the given attribute in the given files'''

    def process_line(line, result_set):
        attribute, value = seria._match_attribute(line)
        if attribute == attribute_name:
            result_set.add(value)

    for filepath, value_set in process_files_by_line(filepaths, process_line):
        print(f'Values for attribute {attribute_name} in file {filepath}:')
        for value in sorted(value_set):
            print(value)


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
        try:
            depth = int(sys.argv[2])
            file_index = 3
        except ValueError:
            depth = None
            file_index = 2

        for filepath in sys.argv[file_index:]:
            try:
                node = seria.load(filepath)
                output_filepath = filepath + '-tree.txt'
                with open(output_filepath, 'w') as file:
                    file.write(seria.tree(node, depth))
                    print(f'Tree structure written to {output_filepath}')
            except IOError:
                logging.error('Could not open file: ' + filepath)
    elif option == '-flagship':
        for filepath in sys.argv[2:]:
            try:
                node = seria.load(filepath)
                creature_node = node.get_node_by_class('Frame').get_node_if(lambda x: x.get_attribute(
                    'm_name') == 'COMBRIDGE').get_node_by_class('Creature')
                creature_node.put_attribute_after(
                    'm_flagship', 'true', 'm_playable')
                seria.dump(node, filepath)
            except IOError:
                logging.error('Could not open file: ' + filepath)
    else:
        logging.error(f'Invalid option: {option}')
        _print_help()
        sys.exit(1)
