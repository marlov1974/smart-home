# P0069 RS485 contract

Experimental M1: USART3 PC10/PC11AF7, PD2 high TX / low RX. Internal HSI16, BRR1667 (~9598baud), fixed96008N1, slave1. DIP and EEPROM configuration are deliberately not interpreted by this first application. Keep/restore existing DIP positions after vendor bootloading.

Supported: Modbus RTU function04, zero-based input address0, quantity1 ->888 (0x0378).

Request: `01 04 00 00 00 01 31 CA`
Response: `01 04 02 03 78 B9 E2`

Read-only existing Shelly path:
`http://192.168.86.85/rpc/MbRtuClient.ReadInputRegisters?id=100&sid=1&addr=0&qty=1`
Expected JSON values:[888]. This input-register read is FC04; naming an address H0 does not change its function code.

Bad CRC, other slave and broadcast: silence. Unsupported function: exception01. Unavailable address/range:02. Invalid quantity:03. No writable registers and no normal Procon telemetry. Frame gap4000us, invalid internal gap>1600us; UART errors/overflow discarded, recovery after silence. PD2 remains high until TC confirms last stop bit; bounded TX wait releases bus on failure. CN105 never initialized or transmitted.

Hardware readback pending operator flash. Six actual-ELF emulation scenarios passed with mocked UART/register behavior; this does not measure actual baud, transceiver or electrical timing.

## M1 r2 correction
Original0x080099CC/CE selects AdvancedInit0x38 (includes SWAP_INIT0x08);0x080099D2/E2 writes Swap0x8000 at UART handle+0x34. ST HAL UART_AdvFeatureInitTypeDef puts Swap there; USART_CR2_SWAP is bit15. Corrected firmware sets CR2=0x8000. Thus AF7 nominal TX/RX are exchanged: PC10 RX,PC11 TX. Initial M1 omitted this and timed out; it is superseded. Evidence is static and test-backed; successful physical readback remains pending. [ST HAL UART definitions](https://github.com/STMicroelectronics/stm32l4xx-hal-driver/blob/master/Inc/stm32l4xx_hal_uart.h).

Final M1 r2: procon/releases/P0069-m1-r2/procon-m1.bin is98304bytes (96KiB),0x08008000–0x0801FFFF, including0xFF padding over the previous original application footprint. Code still limited to16KiB; bootloader excluded. PC12 heartbeat toggles every500ms as startup indication; USART3 SWAP=1. Final BIN SHA2561ad976eef711558ed180a4037e84885f7d74b76175ac2ba0daea0d171f864073. Physical verification pending.
