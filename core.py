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
    if trace:
        print("Set memory address {0} to {1}".format(address, value))
    ram[coerce_value(address)] = coerce_value(value)

def inc(register, n=1):
    "Increment a register, returning the new value"
    new_value = (get_register(register) + n) % 256
    set_register(register, new_value)
    return new_value

def dec(register, n=1):
    "Decrement a register, returning the new value"
    return inc(register, -n)

def inc_ip(n=1):
    "Increment the instruction pointer, returning the new value"
    return inc('ip', n)

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
op_sub = binary_op(lambda x, y: y - x)
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

def op_test(value='a'):
    x = coerce_value(value)
    set_flag('zf', x == 0)
    set_flag('pf', bin(x)[2:].count('1') % 2 == 0)
    set_flag('sf', x < 0)

def op_cmp(x, y='a'):
    op_test(coerce_value(x) - coerce_value(y))

def op_jmp(value='a'):
    "unconditional jump"
    op_mov(value, 'ip')

def jump_if(doc, condition):
    def conditional_jump(value='a'):
        doc
        if condition():
            if trace:
                print("Taking the jump")
            op_mov(value, 'ip')
        else:
            if trace:
                print("Not taking the jump")
    return conditional_jump

op_jo = jump_if("jump if overflow", lambda: get_flag('of'))
op_jno = jump_if("jump if not overflow", lambda: not get_flag('of'))
op_jpe = jump_if("jump if parity is even", lambda: get_flag('pf'))
op_jpo = jump_if("jump if parity is odd", lambda: not get_flag('pf'))

op_jz = jump_if("jump if zero", lambda: get_flag('zf'))
op_jnz = jump_if("jump if not zero", lambda: not get_flag('zf'))
op_jl = jump_if("jump if less", lambda: get_flag('zf') != get_flag('of'))
op_jle = jump_if("jump if less or equal",
        lambda: get_flag('zf') != get_flag('of') or get_flag('zf'))
op_jge = jump_if("jump if greater or equal",
        lambda: get_flag('sf') == get_flag('of'))
op_jaz = jump_if("jump if accumulator is zero",
        lambda: get_register('a') == 0)

def op_push(value='a'):
    x = coerce_value(value)
    stack_pointer = dec('sp') # it grows downward
    set_ram(stack_pointer, x)

def op_pop(register='a'):
    stack_pointer = inc('sp')
    x = get_ram(stack_pointer - 1)
    set_register(register, x)

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

def test_op_sub():
    reset()
    registers['a'] = 100
    op_sub(50)
    check(registers['a'] == 50)

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

def test_cmp():
    reset()
    registers['a'] = 10
    op_cmp(10)
    check(get_flag('zf'))
    check(not get_flag('of'))

    reset()
    registers['a'] = 10
    op_cmp(5)
    check(not get_flag('zf'))
    check(get_flag('sf'))

    reset()
    registers['a'] = 10
    op_cmp(15)
    check(not get_flag('zf'))
    check(not get_flag('sf'))

def test_jmp():
    reset()
    op_jmp(42)
    check(registers['ip'] == 42)

def test_jz():
    reset()
    op_jz()
    check(registers['ip'] == 0)

    reset()
    flags['zf'] = True
    op_jz(42)
    check(registers['ip'] == 42)

def test_push():
    reset()
    op_push(42)
    check(ram[255] == 42)
    check(registers['sp'] == 255)

def test_pop():
    reset()
    ram[254] = 33
    registers['sp'] = 254
    op_pop()
    check(registers['a'] == 33)
    check(registers['sp'] == 255)

def test_operations():
    test_op_not()
    test_op_neg()
    test_op_popcount()
    test_op_clz()
    test_op_store()
    test_op_load()
    test_op_mov()

    test_op_add()
    test_op_sub()
    test_op_mul()
    # test_op_div()
    # test_op_mod()

    test_op_or()
    test_op_and()
    test_op_xor()

    test_cmp()
    test_jmp()
    test_jz()

    test_push()
    test_pop()
    print()

########################################################

def get_operation_by_name(name):
    module = sys.modules[__name__]
    return getattr(module, 'op_' + name)

def run():
    opcode = -1
    instruction = []
    while True:
        opcode = get_ram(get_register('ip'))
        if trace:
            print()
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

        old_ip = get_register('ip')
        fn(*arguments)

        instruction = []

        if old_ip == get_register('ip'):
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

