__author__ = 'Arun'

import os
import json
from optparse import OptionParser
from hashlib import md5

def index(root_directory):
    assert os.path.isdir(root_directory)
    index_dict = {}
    print("Indexing: " + root_directory)

    for folder, subfolders, files in os.walk(root_directory):
        if not os.path.relpath(folder, root_directory) == '.indexer': # this is where indexer stores it's index
            for filename in files:
                filepath = os.path.join(folder, filename)
                rel_path = os.path.relpath(filepath, root_directory) #relative to the root directory
                md5_hash = md5(open(filepath, 'rb').read()).hexdigest()
                print("File: " + rel_path + "  MD5: " + md5_hash)
                index_dict[rel_path] = md5_hash

    output_dir = os.path.join(root_directory, ".indexer")
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    output_file_path = os.path.join(output_dir, "index.json")
    output_file = open(output_file_path, 'w+')
    json.dump(index_dict, output_file)

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
        parser.error("The directory you specified is invalid!")

    if options.index_mode:
        index(options.directory)

if __name__ == '__main__':
    main()