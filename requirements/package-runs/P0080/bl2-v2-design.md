# P0080 BL2 protocol2 identity fix

User authorized build and original-bootloader installation; DIP00000000 ready. Fetch succeeded; local pending P0080 artifacts preserved, continuation rather than merge. Change resident status protocol1→2 and P8 wire version1→2 so old tools/devices cannot silently mix. Manifest fingerprint = CRC32(first56 bytes), used in resident status, BEGIN expected-base check, host plan and postboot check. Stored manifest prefix integrity/slot CRCs stay unchanged. CRC is not authentication.

Functions changed: BL2 normal status, ota_handle version gate/base fingerprint/reply; host frame/decode/plan/status/transfer. Build metadata includes protocol2; planning refuses missing/non-v2 metadata. No layout/export/RAM change. Build bl2/dispatcher/drift revision2 to preserve installed snapshot module bytes, all other modules unchanged. Same original bootloader application envelope,240-byte payload.

Tests: actual ARM resident status CRC/schema; native OTA old-version rejection and valid but wrong base manifest rejection (including constant-residue regression), normal success/duplicate/interrupt/repair; host version mismatch rejection before handoff; unchanged seven chunk comparison; existing ARM flash writer tests. Original physical flash, then operator normal boot needed for read-only final qualification. No FTC controls.
