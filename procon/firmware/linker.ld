/* P0069: conservative subset of inferred L433 flash/SRAM, no bootloader overlap. */
ENTRY(Reset_Handler)
MEMORY {
 FLASH (rx) : ORIGIN = 0x08008000, LENGTH = 16K
 RAM (rwx) : ORIGIN = 0x20000000, LENGTH = 16K
}
_stack_top = ORIGIN(RAM) + LENGTH(RAM);
SECTIONS {
 .isr_vector : { KEEP(*(.isr_vector)) } > FLASH
 .text : { *(.text*) *(.rodata*) . = ALIGN(4); } > FLASH
 .ARM.exidx : { *(.ARM.exidx*) } > FLASH
 .data : { . = ALIGN(4); _data_start = .; *(.data*) . = ALIGN(4); _data_end = .; } > RAM AT> FLASH
 _data_load = LOADADDR(.data);
 .bss (NOLOAD) : { . = ALIGN(4); _bss_start = .; *(.bss*) *(COMMON) . = ALIGN(4); _bss_end = .; } > RAM
 /DISCARD/ : { *(.comment*) *(.note*) }
 ASSERT(ADDR(.isr_vector) == 0x08008000, "Wrong vector base")
 ASSERT(_bss_end + 2048 <= _stack_top, "Insufficient stack")
}
