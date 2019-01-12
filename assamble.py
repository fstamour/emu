#!/usr/bin/env python3

# TODO Add Test and jumps

import sys
from itertools import chain
from meta import register_names, flag_names, operations
from utils import print_dotted_list, params, check, remove_comment
from utils import complement

def compute_codec():
    """Compute "codec" and "opcodes" (used for [dis]assambly)."""
    codec = [None] * len(operations)
    opcodes = {}
    i = 0 
    for operation in operations:
        [op, *operands] = operation.split(' ')
        operands = ''.join(operands)
        name = operation.replace(' ', '')
        length = 1 if operands == 'rr' else len(operands)
        codec[i] = (name, operands, length)
        opcodes[name] = i
        i = i + 1 
    return codec, opcodes

register_codec = register_names + flag_names
codec, opcodes = compute_codec()

###############################################################

def assamble_argument(arg):
    if arg.isdigit():
        arg = int(arg)
        assert arg < 128
        assert arg >= -128
        return arg
    elif arg.startswith("'"):
        assert len(arg) == 3
        return ord(arg[1])
    if arg in register_codec:
        return register_codec.index(arg)
    return ':' + arg

def argument_type(arg):
    if arg.isdigit():
        return 'i'
    elif arg.startswith("'"):
        return 'i'
    elif arg in register_codec:
        return 'r'
    # esle it's a label, which are treated as immediate values
    return 'i'

def test_assamble_argument():
    check(assamble_argument('42') == 42)
    check(assamble_argument("'a'") == 97)
    check(assamble_argument('a') == 0)

def assamble_instruction(line):
    [name, *args] = line.split(' ')
    op = name + ''.join(map(argument_type, args))
    if args == tuple('rr'):
        r1 = assamble_argument(args[0]) 
        r2 = assamble_argument(args[1]) 
        params = [r1 << 4 | r2]
    else:
        params = list(map(assamble_argument, args))

    return [opcodes[op], *params]

def assamble_line(line):
    if ':' in line:
        [label, instruction] = line.split(':')
        result = [label.strip()]
        assert label, "Label cannot be empty."
        instruction = instruction.strip()
        if instruction:
            result += assamble_instruction(instruction)
        return result
    return assamble_instruction(line)

def assamble_lines(code):
    for line in code.split('\n'):
        line = remove_comment(line).strip()
        if line:
            assambled = assamble_line(line.strip())
            yield assambled

def assamble(code):
    return list(chain(*assamble_lines(code)))

def islabel(x):
    return isinstance(x, str) and not x.startswith(':')

def isreference(x):
    return isinstance(x, str) and x.startswith(':')

def link(object_code):
    labels = {}
    position = 0
    for i, element in enumerate(object_code):
        if islabel(element):
            # TODO Check if a label was already defined
            # print("Found label \"{0}\" at position {1}".format(element, position))
            labels[element] = position
        else:
            position += 1
    object_code = list(filter(complement(islabel), object_code))
    for i, element in enumerate(object_code):
        if isreference(element):
            object_code[i] = labels[element[1:]]
    return object_code


def test_assamble():
    assamble("label:")
    obj = assamble("label: jmp label")
    link(obj)

    assamble("cmp 13 # Enter")
    assamble("putc 11 # Linefeed")

###############################################################

def disassamble_arg(arg, operand):
    "Decode 1 arguments, given the operand type expected."
    if operand == 'r':
        return register_codec[arg]
    return arg

def disassamble_arguments(arguments, operands):
    "Decode all the arguments passed to an operations."
    if operands == 'rr':
        r1 = arguments[0] >> 4
        r2 = arguments[0] & 15
        return [register_codec[r1], register_codec[r2]]
    return list(map(disassamble_arg, arguments, operands))

def disassamble_insctruction(instr):
    "Decode a whole assambled instruction."
    [opcode, *arguments] = instr
    [op, operands, length] = codec[opcode]
    if len(arguments) != length:
        return None
    name = op[:-len(operands)] if operands else op
    arguments = disassamble_arguments(arguments, operands)
    return [name, *arguments]

def test_machinery(line):
    parts = line.split(' ')
    encoded = assamble_line(line)
    decoded = list(map(str, disassamble_insctruction(encoded)))
    # print(encoded, decoded, parts) 
    check(decoded == parts)

if __name__ == '__main__': 
    from pprint import pprint

    test_assamble()

    test_machinery('putc')
    test_machinery('neg')
    test_machinery('mov 2')
    test_machinery('mov 2 b')

    # pprint(codec)
    # pprint(opcodes)
    test_assamble_argument()


################# WIP Notes on the density of the code

# Shifts: The parameter of shl and shr < 8 (3 bits)
nops = [
        'div X X', # Divide a register by itself == mov 1 X
        'mov a',   # == mov a a
        'mov X X',
        'xor X X', # Xor a register with itself == mov 0 X
        # The followings are equivalent to they're unary versions
        ['not neg popcount clz', 'a'],
        ['or and xor', 'a'],
]
        
