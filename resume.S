	.text

	mov	r1, #0x56000000
	ldr	r0,[r1, #0xb8]		/* GSTATUS3 */
	mov	pc, r0

