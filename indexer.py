__author__ = 'Arun'

from optparse import OptionParser
import os
from hashlib import md5

def index(directory):
    print("Indexing: " + directory)
    for folder, subfolders, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(folder, filename)
            print(filepath + " MD5: " + md5(open(filepath, 'rb').read()).hexdigest())

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

    if options.index_mode:
        index(options.directory)

if __name__ == '__main__':
    main()