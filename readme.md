# Overly simple virtual machine

> The machine is simple, not the implementation

Implements an had-hoc 8-bits virtual machine, to help teach how computer works.
It includes it own assambler, linker and dissasambler.

## Registers (all 8 bits)

| Name | Description |
| --- | --- |
| a | Accumulator
| b, c, d | General purpose
| ip | Instruction pointer
| sb, sp | Stack base and pointer
| cf | Carry Flag
| pf | Parity Flag
| zf | Zero Flag
| sf | Sign Flag
| of | Overflow Flag

> Note: the registers a, b, c and d behaves as 2's complement integers, but
ip, sb and sp behaves as unsigned integers.

## Instructions

 * getc
 * putc
 * mov
 * add sub mul div mod neg
 * not and or xor shl shr xor
 * halt
 * store/load
 * push/pop
 * cmp
 * test
 * jmp
 * jo jno jz jnz jl jle jge jpe jpo jaz (conditional jumps)

### Not implemented yet

 * call
 * ret
 * rcr rcl rol ror
 * overflow flag

## Hello world

It's possible to run a assembly code that print 'hi' in the terminal: 

```sh
./hi.asm
```
