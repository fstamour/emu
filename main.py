#!/usr/bin/env python3

import sys
from utils import copy
from core import run, reset
import core
from assamble import assamble, link

def slurp(path):
    with open(path, 'r') as file:
        return file.read()

def run_file(path):
    # read the source code from a file
    source_code = slurp(path)

    # assamble (compile) into object code
    obj = assamble(source_code)
    binary = link(obj)

    # initialise the virtual machine
    reset()
    copy(binary, core.ram)

    # !
    run() 
    print()

if __name__ == '__main__':
    # core.trace = True
    run_file(sys.argv[1])

