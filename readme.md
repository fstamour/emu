# Overly simple virtual machine

> The machine is simple, not the implementation

## Registers (all 8 bits)

a       - Accumulator
b, c, d - General purpose
ip      - Instruction pointer
sb, sp  - Stack base and pointer
cf      - Carry Flag
pf      - Parity Flag
zf      - Zero Flag
sf      - Sign Flag
of      - Overflow Flag

## Instructions

 * getc
 * putc
 * mov
 * add sub mul div mod neg
 * not and or xor shl shr xor
 * halt
 * store
 * load

### Not implemented yet

 * push
 * pop
 * call
 * ret
 * rcr rcl rol ror
 * cmp
 * jmp, jXX (two for each flags)
