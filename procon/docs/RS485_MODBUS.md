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
