	.macro putc, ch
        mov     r3, #0x50000000
	add	r3, r3, #0x0000		/* uart offset */
	add	r3, r3, #0x20		/* fifo register */
	mov	r0, \ch
        strb    r0, [r3]

	mov	r1, #0x00020000
1:	subs	r1, r1, #1
	bne	start - . + 1b
	.endm

	.text
start:
	putc	#'H'
	putc	#'e'
	putc	#'l'
	putc	#'l'
	putc	#'o'
	putc	#'\r'
	putc	#'\n'

	b	start - . + start
