/*
 * Prepare for booting a N30 by configuring the hardware and setting
 * up everything the way the Linux kernel expects.
 *
 * On entry, this function file expects the MMU to be off and the
 * following data should be placed directly after it:
 *
 * end+0:         MPLLCON value or zero if it shouldn't be changed
 * end+4:         size of tag data in dwords (must be non zero)
 * end+8:         tag data that should be copied to the start of ram
 * end+8+4*size:  machine type
 * end+12+4*size: the linux kernel entry point
 *
 * Copyright (c) 2005 Christer Weinigel <christer@weinigel.se>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation.
 */

	.text

#define RAM_BASE	0x30000000

#define INTERRUPT_BASE	0x4a000000
#define INTMSK 0x08

#define DMA_BASE	0x4b000000

#define DMASKTRIG0	0x20
#define DMASKTRIG1 	0x60
#define DMASKTRIG2	0xa0
#define DMASKTRIG3	0xe0

#define DMASKTRIG_ON_OFF 2
#define DMASKTRIG_STOP	4

#define CLOCK_BASE	0x4c000000
#define MPLLCON		0x04
#define CLKCON		0x0c

#define USB_BASE	0x52000000
#define EP_INT_EN_REG	0x15c
#define USB_INT_EN_REG	0x16c
#define EP1_DMA_CON	0x200
#define EP2_DMA_CON	0x218
#define EP3_DMA_CON	0x240
#define EP4_DMA_CON	0x258

#define GPIO_BASE	0x56000000

#define EINTMASK	0xa4
#define MISCCR		0x80

// #define ADJUST(offset)	(start - . + offset)
#define ADJUST(offset)	offset

	.text
start:
	/* disable interrupts */
	mrs	r2, cpsr
	orr	r2, r2, #0xc0
	msr	cpsr_c, r2
	
	/* disable mmu and stuff */
	mov	r2, #0
	mcr	p15, 0, r2, c8, c7, 0		/* Invalidate I+D TLB */

	mrc	p15, 0, r2, c1, c0, 0
	bic	r2, r2, #0x000f			/* disable the D-cache + MMU */
	bic	r2, r2, #0x1100			/* disable the I-cache + S */
	mcr	p15, 0, r2, c1, c0, 0

	/* flush caches */

	mov	r1, #(8 - 1) << 5		/* 8 segments */
1:	orr	r2, r1, #(64 - 1) << 26		/* 64 entries */
2:	mcr	p15, 0, r2, c7, c14, 2		/* clean+invalidate D index */
	subs	r2, r2, #1 << 26
	bcs	ADJUST(2b)			/* entries 63 to 0 */
	subs	r1, r1, #1 << 5
	bcs	ADJUST(1b)			/* segments 7 to 0 */
	mov	r1, #0
	mcrne	p15, 0, r1, c7, c10, 4		/* drain write buffer */
	mcrne	p15, 0, r0, c7, c5, 0		/* invalidate I cache */

        /* find the parameters */
#if 0
	/* So why doesn't this work?  is mov reg, pc not defined? */
1:	mov	r4, pc
	add	r4, r4, #end - 1b
#else
	bl	ADJUST(1f)
1:	mov	r4, lr
	add	r4, r4, #end - 1b
#endif

	/* disable USB */
	mov	r0, #GPIO_BASE
	ldr	r1, [r0, #MISCCR]
	bic	r1, r1, #0x3000			/* take USB out of suspend */
	orr	r1, r1, #0x0008			/* select USB host mode */
	str	r1, [r0, #MISCCR]

	/* disable INTMSK */
	mov	r0, #INTERRUPT_BASE
	mvn	r1, #0
	str	r1, [r0, #INTMSK]

	/* disable EINTR */
	mov	r0, #GPIO_BASE
	mvn	r1, #0
	str	r1, [r1, #EINTMASK]

	/* disable DMA */
	mov	r0, #DMA_BASE

	ldr	r1, [r4], #4			/* MPLLCON value */
	subs	r1, r1, #0
	beq	ADJUST(skip_mpllcon)

	mov	r0, #CLOCK_BASE
	str	r1, [r0, #MPLLCON]

	/* TODO fix up the serial port divisors to match the new clock
	 * frequency.  Uncompressing Linux... just ends up like
	 * garbage if the clock frequency is changed. */
skip_mpllcon:
	
	/* tag destination */
	mov	r0, #RAM_BASE
	add	r0, r0, #0x00000100
	mov	r7, r0
	
	ldr	r2, [r4], #4			/* tags size in dwords */

1:	ldr	r3, [r4], #4			/* tag data */
	str	r3, [r0], #4
	subs	r2, r2, #1
	bne	ADJUST(1b)

	mov	r0, #0
	ldr	r1, [r4], #4			/* machine type */
	mov	r2, r7

	mov	pc, r4		/* jump to the kernel after the tags */

	.align	4
end:
