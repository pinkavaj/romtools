	.text

	mov	r1, #0x56000000
	mov	r0, #1
	str	r0, [r1, #0xb4]
	mov	r0, #0
	mov	pc, r0

