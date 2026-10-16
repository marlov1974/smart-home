MEMORY { FLASH(rx): ORIGIN = 0x8013000,LENGTH = 4096
 RAM(rwx): ORIGIN = 0x20003500,LENGTH = 256 }
SECTIONS {
.header : { KEEP(*(.header)) } > FLASH
.exports 0x8013040 : { KEEP(*(.exports)) } > FLASH
.text : { KEEP(*(.layout_probe)) *(.text*) *(.rodata*) . = ALIGN(8); } > FLASH
.data : { _data_start = .; _ramfunc_start = .; *(.ramfunc*) _ramfunc_end = .; *(.data*) . = ALIGN(8); _data_end = .; } > RAM AT> FLASH
_data_load = LOADADDR(.data);
.bss (NOLOAD) : { _bss_start = .; *(.bss*) *(COMMON) . = ALIGN(8); _bss_end = .; } > RAM
/DISCARD/ : { *(.comment*) *(.note*) *(.ARM.exidx*) }
_data_size = _data_end - _data_start; _bss_size = _bss_end - _bss_start;
_stack_top = 0x20004000;
ASSERT(_bss_end <= ORIGIN(RAM)+LENGTH(RAM),"RAM slot overflow")
}
PROVIDE(platform_init = 0x8008201);
PROVIDE(uart_init = 0x8008205);
PROVIDE(uart_receive = 0x8008209);
PROVIDE(uart_send = 0x800820d);
PROVIDE(micros = 0x8008211);
PROVIDE(watchdog_refresh = 0x8008215);
PROVIDE(heartbeat = 0x8008219);
PROVIDE(cn_uart_init = 0x800821d);
PROVIDE(cn_uart_receive = 0x8008221);
PROVIDE(cn_uart_ready = 0x8008225);
PROVIDE(cn_uart_write = 0x8008229);
PROVIDE(platform_uid_word = 0x800822d);
PROVIDE(platform_dip_read = 0x8008231);
PROVIDE(identity_init_dip = 0x8008235);
PROVIDE(modbus_address = 0x8008239);
PROVIDE(identity_read = 0x800823d);
PROVIDE(cn_service = 0x8008241);
PROVIDE(cn_init = 0x800a041);
PROVIDE(cn_feed = 0x800a045);
PROVIDE(cn_tick = 0x800a049);
PROVIDE(cn_tx_byte = 0x800a04d);
PROVIDE(cn_tx_sent = 0x800a051);
PROVIDE(cn_read = 0x800a055);
PROVIDE(cn_command = 0x800a059);
PROVIDE(maintenance_ready = 0x800a05d);
PROVIDE(modbus_reply = 0x800d041);
PROVIDE(ctl_feedback = 0x800e041);
PROVIDE(ctl_link_lost = 0x800e045);
PROVIDE(ctl_init = 0x800e049);
PROVIDE(ctl_observe = 0x800e04d);
PROVIDE(ctl_submit = 0x800e051);
PROVIDE(ctl_tick = 0x800e055);
PROVIDE(ctl_busy = 0x800e059);
PROVIDE(ctl_next = 0x800e05d);
PROVIDE(ctl_reply = 0x800e061);
PROVIDE(ctl_timeout = 0x800e065);
PROVIDE(ctl_read = 0x800e069);
PROVIDE(effect_feedback_init = 0x800e06d);
PROVIDE(effect_feedback_tick = 0x800e071);
PROVIDE(effect_feedback_get = 0x800e075);
PROVIDE(effect_feedback_hard_invalid = 0x800e079);
PROVIDE(tele_snapshot = 0x8011041);
PROVIDE(tele_init = 0x8011045);
PROVIDE(tele_tick = 0x8011049);
PROVIDE(tele_invalidate = 0x801104d);
PROVIDE(tele_accept = 0x8011051);
PROVIDE(tele_read = 0x8011055);
PROVIDE(svc_init = 0x8012041);
PROVIDE(svc_start_cycle = 0x8012045);
PROVIDE(svc_link = 0x8012049);
PROVIDE(svc_tick = 0x801204d);
PROVIDE(svc_due = 0x8012051);
PROVIDE(svc_sent = 0x8012055);
PROVIDE(svc_reply = 0x8012059);
PROVIDE(svc_timeout = 0x801205d);
PROVIDE(svc_bad_frame = 0x8012061);
PROVIDE(svc_read = 0x8012065);
PROVIDE(feedback_read = 0x8014041);
PROVIDE(effect_model_op = 0x8012069);
PROVIDE(effect_model_tick = 0x801206d);
