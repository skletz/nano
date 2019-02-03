#!/usr/bin/env python3
from flask import current_app
import os
import csv
import errno
from datetime import datetime
import ntpath
import shutil
from natsort import natsorted, ns


def make_dir(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Unexpected error: %s", str(e.errno))
            raise  # This was not a "directory exists" error..
        # print("Directory exists: %s", path)
        return False
    return True


def remove_dir(path):
    exists_dir = os.path.isdir(path)
    if exists_dir == True:
        # os.rmdir(path) # does not work if not empty
        shutil.rmtree(path)


def open_file_reading(path):
    return open(path, 'r')


def open_file_writing(path, delete=False):
    exists_file = os.path.isfile(path)
    if delete == True and exists_file == True:
        os.remove(path)
    return open(path, 'a')


def safe_div(x, y):
    """Zero safe division"""
    if y == 0:
        return 0
    return x / y


def get_file_paths(directory):
    retList = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            # print os.path.join(root, filename)
            retList.append(os.path.abspath(os.path.join(root, filename)))
    return retList


def get_directories(directory):
    retList = []
    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            # print os.path.join(root, filename)
            retList.append(os.path.abspath(os.path.join(root, dir)))
    return retList


def get_csv_files(directory):
    retList = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            # print os.path.join(root, filename)
            if (filename.endswith('.csv')):
                retList.append(os.path.abspath(os.path.join(root, filename)))
    return retList


def get_images(directory):
    retList = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            # print os.path.join(root, filename)
            if (filename.endswith('.jpg')):
                retList.append(os.path.abspath(os.path.join(root, filename)))
    return retList


def append_csv(path, lst, cls, root=""):
    myfile = open(path, 'ab')  # 'ab' (binary mode) important for windows!
    # tab would be '\t'
    wr = csv.writer(myfile, delimiter=' ')
    #wr.writerow(('file', 'class'))
    for i in range(len(lst)):
        path = lst[i]
        if root != "":
            path = path.replace(root, "")
        wr.writerow((path, cls))


def append_file(path, lst, prefix="", suffix="", encapsule=""):
    myfile = open(path, 'ab')  # 'ab' (binary mode) important for windows!
    for i in range(len(lst)):
        entry = prefix + encapsule + lst[i] + encapsule + suffix
        myfile.write(entry + "\r\n")


def get_dir_path(file_path):
    return ntpath.dirname(file_path)


def get_immediate_subdirs(a_dir, fullPath=True):
    if not os.path.isdir(a_dir):
        return []
    if fullPath:
        # return filter(os.path.isdir, [os.path.join(a_dir, f) for f in os.listdir(a_dir)])
        return [f.path for f in os.scandir(a_dir) if f.is_dir() ]
    else:
        return [name for name in os.listdir(a_dir)
                if os.path.isdir(os.path.join(a_dir, name))]


def get_last_subdir(file_path):
    if os.path.isfile(file_path):
        filename = ntpath.basename(file_path)
        return ntpath.basename(file_path.replace("/" + filename, ""))
    elif os.path.isdir(file_path):
        return ntpath.basename(file_path)


def get_full_file_name(file_path):
    return ntpath.basename(file_path)


def get_file_name(file_path):
    ff_name = get_full_file_name(file_path)
    file_name, file_extension = os.path.splitext(ff_name)
    return file_name


def get_file_ext(file_path):
    file_name, file_extension = os.path.splitext(file_path)
    return file_extension


def getTimeStamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def get_current_dir():
    return os.getcwd()


def rel_to_abs_path(path):
    current_dir = os.getcwd()
    return os.path.join(current_dir, path)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def nat_sort_list(l):
    return natsorted(l, key=lambda y: y.lower())

def sort_list_nicely(l):
    """ Sort the given list in the way that humans expect.
    """
    def convert(text): return int(text) if text.isdigit() else text

    def alphanum_key(key): return [convert(c)
                                   for c in re.split('([0-9]+)', key)]
    l.sort(key=alphanum_key)

def format_number(number, precision=3, width = 3):
    opts = "{:%s.%sf}" % (str(width), str(precision))
    return opts.format(number)

class switch(object):
    """ This class provides switch functionality.
    """

    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args:  # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False

def printFlaskMsg(msg, is_error = False):
    if (is_error):
        current_app.logger.error(msg)
    else:
        current_app.logger.info(msg)
    # display warning
    # current_app.logger.warning('testing warning log')
