#!./emu
# Demonstrate the use of call and ret
# This should print "5f" and halt

main:
	mov 5
	call print_hex_char
	mov 15
	call print_hex_char
	halt

# prints the register a and 1 hex character
# the value must be between 0 and 15
print_hex_char:
	cmp 10
	jge letter 
	push
	add '0'
	putc
	pop
	ret
letter:
	push
	sub 10
	add 'a'
	putc
	pop

