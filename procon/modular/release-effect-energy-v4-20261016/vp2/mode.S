.syntax unified
.cpu cortex-m4
.thumb
.section .header,"a"
.word 0x50384348,3,1,3833993797,0x800e000,12288, _data_load,_data_start,_data_size,_bss_start,_bss_size,15,2,0,0,0
.section .exports,"ax"
b.w ctl_feedback
b.w ctl_link_lost
b.w ctl_init
b.w ctl_observe
b.w ctl_submit
b.w ctl_tick
b.w ctl_busy
b.w ctl_next
b.w ctl_reply
b.w ctl_timeout
b.w ctl_read
b.w effect_feedback_init
b.w effect_feedback_tick
b.w effect_feedback_get
b.w effect_feedback_hard_invalid
