# P0069. Run make -C procon (no live actions).
TOOLCHAIN ?= .local/arm-gnu-toolchain-14.3.rel1-darwin-arm64-arm-none-eabi
CROSS := $(TOOLCHAIN)/bin/arm-none-eabi-
PYTHON ?= .local/venv/bin/python
CC := $(CROSS)gcc
CFLAGS := -mcpu=cortex-m4 -mthumb -mfloat-abi=soft -std=c11 -Os -g3 -Wall -Wextra -Werror -ffreestanding -fno-builtin -ffunction-sections -fdata-sections -fno-unwind-tables -fno-asynchronous-unwind-tables -Ifirmware/include -ffile-prefix-map=$(CURDIR)=.
SRC := firmware/startup/startup.S firmware/src/main.c firmware/src/platform.c firmware/src/modbus.c
.PHONY: all test verify
all: build/procon-m1.elf build/host-test
	$(PYTHON) tools/check_image.py build/procon-m1.elf $(CROSS)objcopy
	$(CROSS)objdump -d build/procon-m1.elf > build/procon-m1.disasm.txt
	$(CROSS)size build/procon-m1.elf
build:
	mkdir -p build
build/procon-m1.elf: $(SRC) firmware/include/modbus.h firmware/include/platform.h firmware/linker.ld | build
	$(CC) $(CFLAGS) $(SRC) -nostdlib -Wl,--gc-sections,--build-id=none,-Map,build/procon-m1.map -Tfirmware/linker.ld -o $@
build/host-test: tests/test_modbus.c firmware/src/modbus.c firmware/include/modbus.h | build
	clang -std=c11 -g -O1 -Wall -Wextra -Werror -fsanitize=address,undefined -Ifirmware/include tests/test_modbus.c firmware/src/modbus.c -o $@
test: all
	./build/host-test
	$(PYTHON) tests/test_arm.py build/procon-m1.elf
verify: test
	$(PYTHON) tools/analyze_original.py
