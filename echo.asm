#!./emu
# Print back what the user enters until he enters 'q'

loop:
  getc
  putc

  cmp 'q'
  jz halt

  cmp 13 # Enter
  jnz loop
  putc 10 # Line feed

  jmp loop

halt:
  halt

