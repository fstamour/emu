#!./main.py
# Print back what the user enters until he enters 'q'

loop:
  getc
  cmp 'q'
  putc
  jz halt
  jmp loop

halt:
  halt

