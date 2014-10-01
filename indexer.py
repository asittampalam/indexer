#!/usr/bin/env python
__author__ = 'Arun'

import os
import json
from optparse import OptionParser
from hashlib import md5
from fnmatch import fnmatch

# Checks for a list if there is any fnmatch.
def ignore_match(ignore_list, path, quiet = True):
    for elem in ignore_list:
        if fnmatch(path, elem):
            if not quiet:
                print("  Ignoring: " + path)
            return True
    return False

# Creates index (dictionary: relative filepath -> md5 hash) and returns it.
def get_index(root_directory, quiet = True):
    assert os.path.isdir(root_directory)
    index_dict = {}
    ignore_file_path = os.path.join(root_directory, ".indexerignore")
    if not os.path.isfile(ignore_file_path):
        ignore_list = []
    else:
        ignore_file = open(ignore_file_path, "r")
        ignore_list = ignore_file.read().splitlines()


    if not quiet:
        print("Indexing: " + root_directory)

    for folder, subfolders, files in os.walk(root_directory, topdown=True):

        if not os.path.relpath(folder, root_directory) == '.indexer': # this is where indexer stores it's index
            subfolders[:] = [subfolder for subfolder in subfolders if not ignore_match(ignore_list, os.path.relpath(os.path.join(folder, subfolder), root_directory), quiet)] # pruning subfolders we don't want to walk through
            for filename in files:
                filepath = os.path.join(folder, filename)
                rel_path = os.path.relpath(filepath, root_directory) #relative to the root directory

                if not ignore_match(ignore_list, rel_path, quiet):
                    md5_hash = md5(open(filepath, 'rb').read()).hexdigest()
                    if not quiet:
                        print("  File: " + rel_path + "  MD5: " + md5_hash)
                    index_dict[rel_path] = md5_hash
    return index_dict

# Starts index mode:
def start_index_mode(root_directory):
    assert os.path.isdir(root_directory)

    index_dict = get_index(root_directory, False)

    output_dir = os.path.join(root_directory, ".indexer")
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    output_file_path = os.path.join(output_dir, "index.json")
    output_file = open(output_file_path, 'w+')
    json.dump(index_dict, output_file)

# Starts with analyze mode:
def start_analyze_mode(root_directory):
    current_index_dict = get_index(root_directory)
    input_file_path = os.path.join(root_directory, ".indexer", "index.json")
    input_file = open(input_file_path, "r")
    old_index_dict = json.load(input_file)

    difference = DictDiffer(current_index_dict, old_index_dict)

    print("Analyzing: ")

    print(" Unchanged: ")
    for unchanged in difference.unchanged():
        print("  ",unchanged)

    print(" Changed: ")
    for changed in difference.changed():
        print("  ",changed)

    print(" Added: ")
    for added in difference.added():
        print("  ",added)

    print(" Removed: ")
    for removed in difference.removed():
        print("  ",removed)


def main():
    #Parse options
    parser = OptionParser()
    parser.add_option("-d", "--directory", dest="directory", help="specify directory")
    parser.add_option('-i', '--index', help='index mode', dest='index_mode', default=False, action='store_true')
    parser.add_option('-a', '--analyze', help='analyze mode', dest='analyze_mode', default=False, action='store_true')

    (options, args) = parser.parse_args()
    if options.index_mode == options.analyze_mode:
        parser.error('You have to choose a mode!')

    if not options.directory:
        options.directory = os.getcwd()

    options.directory = os.path.abspath(options.directory)

    if not os.path.isdir(options.directory):
        parser.error("The directory you specified is invalid! (" + options.directory +")")

    if options.index_mode:
        start_index_mode(options.directory)
    else:
        start_analyze_mode(options.directory)


# Nice little class from http://stackoverflow.com/questions/1165352/fast-comparison-between-two-python-dictionary:
# Allows efficient comparison of two dicts.
class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)
    def added(self):
        return self.set_current - self.intersect
    def removed(self):
        return self.set_past - self.intersect
    def changed(self):
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])
    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])

if __name__ == '__main__':
    main()