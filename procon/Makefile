# P0069. Run make -C procon (no live actions).
TOOLCHAIN ?= .local/arm-gnu-toolchain-14.3.rel1-darwin-arm64-arm-none-eabi
CROSS := $(TOOLCHAIN)/bin/arm-none-eabi-
PYTHON ?= .local/venv/bin/python
CC := $(CROSS)gcc
CFLAGS := -mcpu=cortex-m4 -mthumb -mfloat-abi=soft -std=c11 -Os -g3 -Wall -Wextra -Werror -ffreestanding -fno-builtin -ffunction-sections -fdata-sections -fno-unwind-tables -fno-asynchronous-unwind-tables -Ifirmware/include -ffile-prefix-map=$(CURDIR)=.
SRC := firmware/startup/startup.S firmware/src/main.c firmware/src/platform.c firmware/src/modbus.c firmware/src/cn105.c
.PHONY: all test verify
all: build/procon-compressor.elf build/host-test build/cn-test
	$(PYTHON) tools/check_image.py build/procon-compressor.elf $(CROSS)objcopy
	$(CROSS)objdump -d build/procon-compressor.elf > build/procon-compressor.disasm.txt
	$(CROSS)size build/procon-compressor.elf
build:
	mkdir -p build
build/procon-compressor.elf: $(SRC) firmware/include/modbus.h firmware/include/platform.h firmware/include/cn105.h firmware/linker.ld | build
	$(CC) $(CFLAGS) $(SRC) -nostdlib -Wl,--gc-sections,--build-id=none,-Map,build/procon-compressor.map -Tfirmware/linker.ld -o $@
build/host-test: tests/test_modbus.c firmware/src/modbus.c firmware/src/cn105.c firmware/include/modbus.h firmware/include/cn105.h | build
	clang -std=c11 -g -O1 -Wall -Wextra -Werror -fsanitize=address,undefined -Ifirmware/include tests/test_modbus.c firmware/src/modbus.c firmware/src/cn105.c -o $@
build/cn-test: tests/test_cn105.c firmware/src/cn105.c firmware/include/cn105.h | build
	clang -std=c11 -g -O1 -Wall -Wextra -Werror -fsanitize=address,undefined -Ifirmware/include tests/test_cn105.c firmware/src/cn105.c -o $@
test: all
	./build/host-test
	./build/cn-test
	$(PYTHON) tests/test_arm.py build/procon-compressor.elf
verify: test
	$(PYTHON) tools/analyze_original.py
