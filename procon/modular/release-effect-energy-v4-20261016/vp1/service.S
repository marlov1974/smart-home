.syntax unified
.cpu cortex-m4
.thumb
.section .header,"a"
.word 0x50384348,5,1,3833993797,0x8012000,4096, _data_load,_data_start,_data_size,_bss_start,_bss_size,10,2,0,0,0
.section .exports,"ax"
b.w svc_init
b.w svc_start_cycle
b.w svc_link
b.w svc_tick
b.w svc_due
b.w svc_sent
b.w svc_reply
b.w svc_timeout
b.w svc_bad_frame
b.w svc_read
b.w effect_model_op
b.w effect_model_tick
