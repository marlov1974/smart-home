.syntax unified
.cpu cortex-m4
.thumb
.section .header,"a"
.word 0x50384348,4,1,3833993797,0x8011000,4096, _data_load,_data_start,_data_size,_bss_start,_bss_size,6,2,0,0,0
.section .exports,"ax"
b.w tele_snapshot
b.w tele_init
b.w tele_tick
b.w tele_invalidate
b.w tele_accept
b.w tele_read
