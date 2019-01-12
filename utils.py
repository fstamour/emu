import sys
import tty, termios
import traceback 

def print_dotted_list(lis):
    for i in lis:
        print('  *', i)

# Not sure this works on windows
def getchar():
    "Read one keypress from the terminal"
    stdin = sys.stdin.fileno()
    old = termios.tcgetattr(stdin)
    new = termios.tcgetattr(stdin)
    try:
        tty.setraw(stdin)
        new[3] = new[3] & ~termios.ECHO
        char = sys.stdin.read(1)
    finally:
        termios.tcsetattr(stdin, termios.TCSADRAIN, old)
    return ord(char)

def putchar(value):
    "Take an ascii value and print it."
    sys.stdout.write(chr(value))
    sys.stdout.flush()

def check(passed):
    "Print the traceback if passed is false, print a dot (without newline) otherwise."
    if not passed:
        print("Check failed")
        traceback.print_stack()
    else:
        sys.stdout.write('.')

def fix_overflow(x):
    if x < 128:
        return x
    return (x % 128) - 128

assert fix_overflow(128) == -128
assert fix_overflow(127) == 127
assert fix_overflow(-128) == -128
assert fix_overflow(0) == 0
assert fix_overflow(150) == -106

def fix_underflow(x):
    if x >= -128:
        return x
    return x % 128

assert fix_underflow(127) == 127
assert fix_underflow(-128) == -128
assert fix_underflow(0) == 0
assert fix_underflow(-200) == 56

def params(fn):
    "Get a list of tuples representing the arguments of a function."
    varnames = list(fn.__code__.co_varnames)
    arguments = varnames[:fn.__code__.co_argcount]
    defaults = list(fn.__defaults__)
    defaults.extend([None] * (len(arguments) - len(defaults)))
    return list(zip(arguments[::-1], defaults))[::-1]

def popcount(n):
    "count the number of 1s in binary representation"
    return bin(n).count('1')

def count_leading_zeros(n):
    "count the number of leading zeros in binary representation"
    bin_str = bin(n)[2:].zfill(8)
    return 8 - len(bin_str.lstrip('0'))

def remove_comment(line):
    "remove the '#' and after"
    if '#' in line:
        return line[:line.index('#')]
    return line

def copy(source, destination, destination_start = 0):
    "copy a sequence over a list, from a certain place."
    i = 0
    for s in source:
        destination[destination_start + i] = s
        i = i + 1

def complement(fn):
    def comp(x):
        return not fn(x)
    return comp
