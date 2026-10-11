# P0086 — clock, framing and packet reference

Static 20.01. Analytical framing **PASS**, absolute clock **PARTIAL**, physical **NOT RUN**. Confidence CONFIRMED for register writes/packet paths; conditional clock calculations are STRONG HYPOTHESIS pending exact MCU/oscillator identification.

9156E writesCM0=08,CM1=20,CM2=81,PCLKR=03. 910E4 clears CM2bit1, writesPLC0=24 then enablesbit7 (A4), waits via TimerB0, selectsPLL withCM1bit1, ends CM1=22 and clearsCM0bit6. Under M16C/65 hardware manual R01UH0135EJ0210 pp104–106, PLC0=24 means input divide4/multiply8, i.e. PLL=2×external clock. PCLKRbit1=1 selectsf1SIO. UART1C0 lowbits00 andBRG=CF give `baud=f1SIO/(16*(207+1))=f1SIO/3328`. UART2 C0 lowbits01/BRG67 givesf1SIO/13312, one quarter. With16MHz external and32MHz f1SIO, UART1=9615.38bps, plausible nominal9600; this is not a measured or selected live baud. Exact oscillator, silicon/package and clock variants remain unresolved. No baud sweep is implemented.

9E642: UART1MR=65 (8E1),C0=10 (no CTS/RTS flow control in this setup),BRG=CF. 8AF86:MR=15 (8N2),sameBRG. Internal polarity normal; external inversion/transceiver/half-duplex UNKNOWN. UART register 0258/0259/025A/025E belongs to UART1, distinct from UART2 at0268. MCU logic levels are not connector supply levels.

RX9E66E collects5bytes into3D56..5A, requires sum modulo256=0, copies to3D4E..52 and flags3D4D. UART025Fbit7 signals receive error.9E718 handles overrunbit4 and resets receiver/partial state.9E760 increments a partial-receive timer; threshold>5 is in task ticks, not proven seconds. Wrong checksum/partial frame has no success response. Busy requests have no qualified queue/retry guarantee.

## Complete diagnostic vectors (offline static profile only)

| Operation | Five request bytes | Expected response |
|---|---|---|
|Open|00 00 00 00 00|00 03 FD|
|Read candidate RAM0400,1byte|01 00 04 00 FB|01 04 xx cc; sum=0|
|Drain logs|02 F0 00 00 0E|02 4D F0 02 +72 record bytes +checksum|
|Close|0F 00 00 00 F1|No reply; silence does not prove closure|
|Rejected diagnostic operation|not generated|0F 03 EE error response|

9E77A dispatches low nibble:0 sets session3D4C=1;1/2 require session1 and TXidle3D53=0; othernibbles clear session. Memory high nibble indexes832BE length table `1,2,4,8,16,32,64,1,1,1,1,1,1,1,1,1`. Address bytes1..3 little-endian. Canonical tool uses indices0..6 only. Operation2 highnibble0 dispatches9D88C;highnibble1 dispatches9DAC0 (not implemented beyond established log path). Unknown subcommands are not generated.

9E8B4 clears output;9E91C builds open response;9E938 builds memory response ofN+3 bytes;9E92A emits error.9E8E0 appends negative checksum over length-1bytes.9E850/9E87A transmit total length1347 from1346. Codec bounds responses to77bytes, validates exact operation/length/checksum, and rejects unexpected error frames. No automatic retry: open/close semantics and destructive log drain are not treated as idempotent. Host deadlines are policy, not derived firmware timeout.
