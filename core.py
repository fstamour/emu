#!/usr/bin/env python3
#
#  Emulator for a very small 8-bit machine
#

import sys
from assamble import register_names, flag_names, opcodes, codec
from assamble import assamble, disassamble_insctruction
from utils import getchar, putchar, check, fix_overflow, fix_underflow
from utils import popcount, count_leading_zeros, copy

ram_size = 256
ram = None
registers = None
flags = None
trace = False

def reset():
    global ram
    global registers
    global flags
    ram = [0] * ram_size
    registers = {name: 0 for name in register_names}
    flags = {name: 0 for name in flag_names}

def dump():
    print(ram)
    print(registers)
    print(flags)

def get_register(register):
    "Get a register's content."
    assert register in register_names
    return registers[register]

def get_flag(flag):
    "Get a flag's value"
    assert flag in flag_names
    return 1 if flags[flag] else 0

def get_register_or_flag(name):
    "Get a flag or a register's value."
    if name in register_names:
        return get_register(name)
    elif name in flag_names:
        return get_flag(name)
    raise NameError("Invalid register or flag name: \"{0}\"".format(name))

def coerce_value(x):
    "Return either x of the register specified by x."
    if not isinstance(x, str):
        return x
    return get_register_or_flag(x)

def get_ram(address):
    return ram[coerce_value(address)]

def set_register(register, value):
    "Set a register, the value can either be an int or a register name."
    assert register in register_names
    x = coerce_value(value)
    if trace:
        print("Set register {0} to {1}".format(register, x))
    registers[register] = x

def set_flag(flag, value):
    assert flag in flag_names
    p = not (value == 0)
    if trace and flags[flag] != p:
        print("Set flag {0} to {1}".format(flag, p))
    flags[flag] = p
    
def set_register_or_flag(name, value):
    "Name can either be a register or a flag, value must be an int."
    if name in register_names:
        set_register(name, value)
    elif name in flag_names:
        set_register(name, value)
    else:
        raise NameError("Invalid register or flag name: \"{0}\"".format(name))

def set_ram(address, value):
    ram[coerce_value(address)] = coerce_value(value)

def acc(value=None):
    "Small helper, to use the accumulator register."
    if value is None:
        return get_register('a')
    set_register('a', value)

########################################################### 
################### Operations ############################ 
########################################################### 

# -[x] add
# -[x] and
# -[x] div
# -[x] getc
# -[x] load
# -[x] mod
# -[x] mov
# -[x] mul
# -[x] neg
# -[x] not
# -[x] or
# -[x] popcount
# -[x] putc
# -[ ] rcl
# -[ ] rcr
# -[ ] rol
# -[ ] ror
# -[x] shl
# -[x] shr
# -[x] store
# -[x] sub
# -[x] xor

def unary_op(fn):
    def op(value='a', register='a'):
        x = coerce_value(value)
        set_register(register, fn(x))
    return op

def binary_op(fn):
    def op(value='a', register='a'):
        x = coerce_value(value)
        y = get_register(register)
        result = fn(x, y)
        result = fix_overflow(fix_underflow(result))
        set_register(register, result)
    return op

########################################################

def op_getc(register='a'):
    set_register(register, getchar())

def op_putc(value='a'):
    putchar(coerce_value(value))

op_not = unary_op(lambda x: ~x)
op_neg = unary_op(lambda x: fix_overflow(fix_underflow(-x)))

op_popcount = unary_op(popcount)
op_clz = unary_op(count_leading_zeros)

op_add = binary_op(lambda x, y: x + y)
op_sub = binary_op(lambda x, y: x - y)
op_mul = binary_op(lambda x, y: x * y)
op_div = binary_op(lambda x, y: x / y)
op_mod = binary_op(lambda x, y: x % y)

op_or = binary_op(lambda x, y: x | y)
op_and = binary_op(lambda x, y: x & y)
op_xor = binary_op(lambda x, y: x ^ y)

op_shl = binary_op(lambda x, y: x << y)
op_shr = binary_op(lambda x, y: x >> y)

def op_store(address, value='a'):
    set_ram(address, value)

def op_load(address='a', register='a'):
    value = get_ram(address)
    set_register(register, value)

def op_mov(value='a', register='a'):
    set_register(register, coerce_value(value))

def test(value='a'):
    x = coerce_value(value)
    set_flag('zf', x == 0)
    set_flag('pf', bin(x)[2:].count('1') % 2 == 0)
    set_flag('sf', x < 0)

########################################################

def test_op_not():
    trace = True
    reset()
    registers['b'] = 42
    op_not('b')
    check(registers['a'] == -43)

    reset()
    registers['a'] = 42
    op_not()
    check(registers['a'] == -43)
    trace = False

def test_op_neg():
    reset()
    registers['a'] = 127
    op_neg()
    check(registers['a'] == -127)

    reset()
    registers['a'] = -128
    op_neg()
    check(registers['a'] == -128)

    reset()
    registers['a'] = 2
    op_neg()
    check(registers['a'] == -2)

def test_op_popcount():
    reset()
    registers['b'] = 42
    op_popcount('b', 'c')
    check(registers['c'] == 3)

    reset()
    registers['b'] = 42
    op_popcount('b')
    check(registers['a'] == 3)

    reset()
    registers['a'] = 42
    op_popcount()
    check(registers['a'] == 3)

    reset()
    op_popcount(42)
    check(registers['a'] == 3)

def test_op_clz():
    reset()
    op_clz(42)
    check(registers['a'] == 2)

def test_op_store():
    reset()
    op_store(1, 2)
    check(ram[1] == 2)

    reset()
    registers['a'] = 3
    op_store('a', 2)
    check(ram[3] == 2)

    reset()
    registers['b'] = 2
    op_store(3, 'b')
    check(ram[3] == 2)

    reset()
    registers['a'] = 3
    registers['b'] = 2
    op_store('a', 'b')
    check(ram[3] == 2)

def test_op_load():
    reset()
    ram[3] = 2
    op_load(3)
    check(registers['a'] == 2)

    reset()
    ram[3] = 2
    op_load(3, 'b')
    check(registers['b'] == 2)

    reset()
    ram[3] = 2
    registers['b'] = 3
    op_load('b')
    check(registers['a'] == 2)

    reset()
    ram[3] = 2
    registers['b'] = 3
    op_load('b', 'c')
    check(registers['c'] == 2)

    reset()
    ram[3] = 2
    registers['a'] = 3
    op_load()
    check(registers['a'] == 2)

def test_op_mov():
    reset()
    op_mov(3, 'b')
    check(registers['b'] == 3)

    reset()
    registers['b'] = 3
    op_mov('b', 'c')
    check(registers['c'] == 3)

    reset()
    op_mov(3)
    check(registers['a'] == 3)

    reset()
    registers['b'] = 3
    op_mov('b')
    check(registers['a'] == 3)

def test_op_add():
    reset()
    registers['a'] = 4
    op_add()
    check(registers['a'] == 8)

    reset()
    registers['a'] = 4
    op_add(3)
    check(registers['a'] == 7)

    reset()
    registers['a'] = 4
    op_add('a', 'b')
    check(registers['b'] == 4)

    reset()
    op_add(3, 'b')
    check(registers['b'] == 3)

    # overflow
    reset()
    registers['a'] = 127
    op_add()
    check(registers['a'] == -2)

    # underflow
    reset()
    registers['a'] = -128
    op_add()
    check(registers['a'] == 0)

def test_op_mul():
    reset()
    registers['a'] = 5
    op_mul(2)
    check(registers['a'] == 10)

def test_op_or():
    reset()
    registers['a'] = 2
    registers['b'] = 1
    op_or('b')
    check(registers['a'] == 3)

def test_op_and():
    reset()
    registers['a'] = 2
    registers['b'] = 1
    op_and('b')
    check(registers['a'] == 0)

    reset()
    registers['a'] = 2
    registers['b'] = 3
    op_and('b')
    check(registers['a'] == 2)

def test_op_xor():
    reset()
    registers['a'] = 42
    op_xor()
    check(registers['a'] == 0)

    reset()
    registers['a'] = 2
    registers['b'] = 3
    op_xor('b')
    check(registers['a'] == 1)

def test_operations():
    test_op_not()
    test_op_neg()
    test_op_popcount()
    test_op_clz()
    test_op_store()
    test_op_load()
    test_op_mov()

    test_op_add()
    # test_op_sub()
    test_op_mul()
    # test_op_div()
    # test_op_mod()

    test_op_or()
    test_op_and()
    test_op_xor()
    print()

########################################################

def inc_ip(n=1):
    "Increment the instruction pointer"
    set_register('ip', get_register('ip') + n)

def get_operation_by_name(name):
    module = sys.modules[__name__]
    return getattr(module, 'op_' + name)

def run():
    opcode = -1
    instruction = []
    while opcode != 0:
        opcode = get_ram(get_register('ip'))
        if trace:
            print("Read opcode {0}".format(opcode))
        instruction.append(opcode)
        code = disassamble_insctruction(instruction)

        # Not done reading the instruction
        if code is None:
            inc_ip()
            continue

        if trace: 
            print("Running instruction: ", code)


        [op, *arguments] = code
        if op == 'halt':
            return
        fn = get_operation_by_name(op)
        fn(*arguments)

        instruction = []
        inc_ip()

def test_run():
    # global trace
    # trace = True
    reset();

    obj = assamble("""
    mov 'h'
    putc
    mov 'i'
    putc
    halt
    """) 
    copy(obj, ram)

    run()

if __name__ == '__main__':
    test_operations()
    test_run()

