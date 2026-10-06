# Procon firmware development

Subproject of Smart Home; no nested repository. First experimental clean-source M1 candidate is in [releases/P0069-m1-r2](releases/P0069-m1-r2/README.md).

**Input register0 =888**, Modbus FC04/slave1/96008N1. STM32L433 hardware inferred from original reference, not physically identified. Software/ARM emulation checks passed; physical flash/readback pending operator. CN105 is not implemented.

```sh
sh procon/tools/setup.sh
make -C procon verify
```

Read docs/HARDWARE.md, docs/TOOLCHAIN.md and docs/RECOVERY.md. CODEX_TASK.md is the milestone scope; P0069 records the user's explicit permission to proceed with an inferred MCU and operator-managed physical flash. Original ZIP/BIN remain immutable under reference/original. Do not broaden beyond M1 until hardware readback succeeds.

M1 first physical readback failed (seven timeouts). r2 corrects proven USART3 TX/RX SWAP omission; updated ARM wiring test rejects first ELF and passes r2. Physical r2 result pending.
