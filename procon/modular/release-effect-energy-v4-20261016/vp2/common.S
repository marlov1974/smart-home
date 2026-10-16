.syntax unified
.cpu cortex-m4
.thumb
.section .header,"a"
.word 0x50384348,1,1,3833993797,0x800a000,12288, _data_load,_data_start,_data_size,_bss_start,_bss_size,8,2,0,0,0
.section .exports,"ax"
b.w cn_init
b.w cn_feed
b.w cn_tick
b.w cn_tx_byte
b.w cn_tx_sent
b.w cn_read
b.w cn_command
b.w maintenance_ready
