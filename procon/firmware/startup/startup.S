/* P0069. Fresh polling-only Cortex-M4 application startup. */
.syntax unified
.cpu cortex-m4
.thumb
.section .isr_vector,"a",%progbits
.global vectors
vectors:
 .word _stack_top
 .word Reset_Handler
 .rept 97
 .word Default_Handler
 .endr
.section .text.Reset_Handler,"ax",%progbits
.global Reset_Handler
.type Reset_Handler,%function
.thumb_func
Reset_Handler:
 cpsid i
 ldr r0, =_stack_top
 mov sp, r0
 movs r0, #0
 msr control, r0
 isb
 ldr r0, =0xe000ed08
 ldr r1, =vectors
 str r1, [r0]
 dsb
 isb
 ldr r0, =_data_load
 ldr r1, =_data_start
 ldr r2, =_data_end
1: cmp r1, r2
 bhs 2f
 ldr r3, [r0], #4
 str r3, [r1], #4
 b 1b
2: ldr r1, =_bss_start
 ldr r2, =_bss_end
 movs r3, #0
3: cmp r1, r2
 bhs 4f
 str r3, [r1], #4
 b 3b
4: bl main
 b Default_Handler
.size Reset_Handler, .-Reset_Handler
.section .text.Default_Handler,"ax",%progbits
.global Default_Handler
.type Default_Handler,%function
.thumb_func
Default_Handler:
 ldr r0, =0x48000c18
 ldr r1, =0x40000
 str r1, [r0]
5: b 5b
.size Default_Handler, .-Default_Handler
