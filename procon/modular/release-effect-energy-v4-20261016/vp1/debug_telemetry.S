.syntax unified
.cpu cortex-m4
.thumb
.section .header,"a"
.word 0x50384348,7,1,3833993797,0x8014000,4096, _data_load,_data_start,_data_size,_bss_start,_bss_size,1,1,0,0,0
.section .exports,"ax"
b.w feedback_read
