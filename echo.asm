#!./main.py

loop:
  getc
  cmp 'q'
  putc
  jz halt
  jmp loop

halt:
  halt

