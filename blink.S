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
	mov	r3,#0x56000000
	ldr	r0,[r3, #0x30]
	bic	r0, r0, #0x30000
	orr	r0, r0, #0x10000
	str	r0,[r3, #0x30]

again:
	ldr	r0,[r3, #0x34]
	bic	r0, r0, #0x100
	str	r0,[r3, #0x34]

	mov	r1, #0x40000
1:	subs	r1, r1, #1
	bne	start - . + 1b

	ldr	r0,[r3, #0x34]
	orr	r0, r0, #0x100
	str	r0,[r3, #0x34]

	mov	r1, #0x40000
1:	subs	r1, r1, #1
	bne	start - . + 1b

	b	again - . + start
