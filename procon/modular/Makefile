# P0080 offline build; test-arm needs Python Unicorn and pyelftools.
PYTHON ?= python3
TOOLCHAIN ?= /tmp/procon-export/.local/toolchain
.PHONY: all test test-arm
all:
	$(PYTHON) build.py --toolchain $(TOOLCHAIN)
test: all
	$(MAKE) -f Makefile.baseline host-test PYTHON=$(PYTHON)
	$(PYTHON) build.py --toolchain $(TOOLCHAIN) --out build-next --change-slot service --revision 2 --probe-slot service
	clang -shared -fPIC -std=c11 -Wall -Wextra -Werror -Ifirmware/include -Ibuild firmware/src/ota.c tests/ota_backend.c -o build/ota-test.dylib
	$(PYTHON) tests/test_ota.py
	$(PYTHON) tests/test_sender.py
	$(PYTHON) tests/test_shelly_core.py
test-arm: all
	$(PYTHON) tests/test_modules_arm.py build
	$(PYTHON) tests/test_flash_ram_arm.py build/bl2.elf
	$(PYTHON) tests/test_arm.py build/bl2.elf

# Protocol2 BL2 replacement preserves every installed snapshot feature chunk.
.PHONY: bl2-v2 bl2-v2-test
bl2-v2:
	$(PYTHON) build.py --toolchain $(TOOLCHAIN) --out build-bl2-v2 --change-slot bl2,drift,dispatcher --revision 2
bl2-v2-test: bl2-v2
	$(PYTHON) build.py --toolchain $(TOOLCHAIN) --out build-bl2-v2-next --change-slot bl2,drift,dispatcher,service --revision 2 --probe-slot service
	clang -shared -fPIC -std=c11 -Wall -Wextra -Werror -Ifirmware/include -Ibuild-bl2-v2 firmware/src/ota.c tests/ota_backend.c -o build-bl2-v2/ota-test.dylib
	P80_OTA_LIB=build-bl2-v2/ota-test.dylib P80_OTA_OLD=build-bl2-v2 P80_OTA_NEW=build-bl2-v2-next P80_OTA_RESULT=build-bl2-v2/ota-results.json $(PYTHON) tests/test_ota.py
	P80_OTA_LIB=build-bl2-v2/ota-test.dylib P80_OTA_OLD=build-bl2-v2 P80_OTA_NEW=build-bl2-v2-next $(PYTHON) tests/test_sender.py
	$(PYTHON) tests/test_snapshot_arm.py build-bl2-v2
	$(PYTHON) tests/test_flash_ram_arm.py build-bl2-v2/bl2.elf
