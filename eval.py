#!/usr/bin/env python3
#
# Evaluate an assembly file
# (not the same as running the virtual machine)
#

import sys
from meta import register_names, flag_names
from utils import remove_comment
import core

def get_operation_by_name(name):
    module = sys.modules['core']
    return getattr(module, 'op_' + name)

def parse_argument(arg):
    if arg.isdigit():
        arg = int(arg)
        assert arg < 128
        assert arg >= -128
    elif arg.startswith("'"):
        assert len(arg) == 3
        return ord(arg[1])
    else:
        assert arg in (register_names + flag_names)
    return arg

def parse_instruction(line):
    [op, *args] = line.split(' ')
    assert op
    return op, list(map(parse_argument, args))

def eval_line(line):
    op, args = parse_instruction(remove_comment(line).strip()) 
    fn = get_operation_by_name(op)
    fn(*args)

def eval_code(code):
    for line in code.split('\n'):
        if remove_comment(line).strip():
            if core.trace:
                print('> ', line.strip())
            eval_line(line)
            core.test()

core.trace = True
if __name__ == '__main__':
    core.reset()
    eval_code("""
    mov 'h' a 
    putc
    mov 'i' a 
    putc
    """)

