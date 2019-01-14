#!/usr/bin/env python3

# TODO Add Test and jumps

import sys
from itertools import chain
from utils import print_dotted_list

register_names = ['a', 'b', 'c', 'd', 'ip', 'sb', 'sp'] # 7 registers
flag_names = ['cf', 'pf', 'zf', 'sf', 'of']             # 5 flags
                                                        # => 12
# getc putc
# not neg popcount clz
# add sub mul div mod
# or and xor shl shr
# store load mov
operations = [
        'halt',
        ['getc putc'],
        ['getc putc', 'r'],
        'putc i',
        ['not neg popcount clz'],
        ['not neg popcount clz', 'r'],
        ['add sub mul div mod'],
        ['add sub mul div mod', 'i'],
        ['add sub mul div mod', 'r'],
        ['add sub mul div mod', 'r r'],
        ['add sub mul div mod', 'i r'],
        ['or and xor shl shr'],
        ['or and xor shl shr', 'i'],
        ['or and xor shl shr', 'r'],
        ['or and xor shl shr', 'r r'],
        ['or and xor shl shr', 'i r'],
        'store i',
        'store r',
        'store i i',
        'store r i',
        'store r r',
        'store i r',
        'load i',
        'load r',
        'load i r',
        'load r r',
        'mov i',
        'mov r',
        'mov r r',
        'mov i r',
        'test r',
        'cmp i',
        'cmp r',
        'cmp i, r',
        'cmp r, r',
        'jmp i',
        'jmp r',
        ['jo jno jz jnz jl jle jge jpe jpo jaz', 'i'],
        'push',
        'push i',
        'push r',
        'pop',
        'pop r',
        'call i',
        'call r',
        'ret'
    ]

def expand(spec):
    """Used to flatten the "operations" list"""
    if isinstance(spec, list):
        [ops, *arg] = spec
        ops = ops.split(' ')
        for op in ops:
            if arg:
                yield op + ' ' + arg[0]
            else:
                yield op
    else:
        yield spec

operations = list(chain(*map(expand, operations)))

if __name__ == '__main__':
    print_dotted_list(operations)
    print("There are {0} different operations.".format(len(operations)))
