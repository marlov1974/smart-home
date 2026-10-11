# P0082 toolchain

Installed and executed on Apple Silicon arm64, macOS 26.6.2, Xcode command-line tools present; approximately 159 GiB free before installation. Java was initially absent; no Homebrew was found on PATH. No sudo used. Install is reversible under local workspace `P0082/tools`; Ghidra additionally creates normal user preferences/cache.

- [Official Ghidra 12.1.4 release](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.4_build): `ghidra_12.1.4_PUBLIC_20260921.zip`, SHA-256 `ddac49f903da9d5bac833e5cc79395098b9c33cfd3279be5f31bd00387d2d4db`, verified against release digest before extraction.
- [Version-pinned requirements](https://github.com/NationalSecurityAgency/ghidra/blob/Ghidra_12.1.4_build/GhidraDocs/GettingStarted.md) require JDK 21. Do not use master's newer JDK requirement as release truth.
- [Official Temurin archive](https://github.com/adoptium/temurin21-binaries/releases/tag/jdk-21.0.12.1%2B1): `OpenJDK21U-jdk_aarch64_mac_hotspot_21.0.12.1_1.tar.gz`, SHA-256 `3623232f33a9c3baadf304480b2535f9a3cba8a58d42ecbb438ba267315d9998`, verified against Adoptium API checksum. Actual Java output: 21.0.12.1+1-LTS.
- Official native build: `JAVA_HOME=<jdk>/Contents/Home <ghidra>/support/gradle/gradlew -p <ghidra>/support/gradle buildNatives`; BUILD SUCCESSFUL, 14 tasks. Wrapper downloaded Gradle 9.7.1. Mac native components are not bundled in the release.
- [esaulenka/ghidra_m16c](https://github.com/esaulenka/ghidra_m16c/tree/2833a30bf0ba5b9ac9b2e472966b4bc04d4f71cc), pinned `2833a30bf0ba5b9ac9b2e472966b4bc04d4f71cc`.
- [silverchris/m16c](https://github.com/silverchris/m16c/tree/a67013a617ddd82d4f04ebf31c2752f82f99e2d0), pinned `a67013a617ddd82d4f04ebf31c2752f82f99e2d0`. Their `data` trees are byte-identical at these revisions. Neither checkout has an explicit license file: third-party module source is installed locally, not republished.

Install module by copying its directory into `<ghidra>/Ghidra/Extensions/`; language is `m16c:LE:16:default`, little endian, 16-bit operand model, 32-bit Ghidra RAM space containing the MCU's 20-bit addresses. SLEIGH compiles with 20 empty-semantics constructors and four redundant-extension warnings. A decompiler warning at 0x9B038 remains. Coverage is partial, not a fully validated emulator.

Known-vector fixture: 04 NOP, F3 RTS, FB REIT, FC 40 55 0D JMP.A D5540. Mnemonics/lengths/absolute operand decode correctly. **Unmodified module emits no static flow for the absolute jump.** Two attempted local SLEIGH fixes failed compilation and were reverted. `P82Audit.java` instead resolves a bounded set of documented direct encodings in already-decoded instructions. Its inferred edges are explicitly user-defined, not hardware proof. Native indirect calls remain incomplete.

Portable invocation: set GHIDRA_HOME, JAVA_HOME, FTC6_MOT and LOCAL_OUT, then `sh tools/ftc6/run-analysis.sh`. Use a new LOCAL_OUT for a repeat. Full Ghidra projects, instructions and reference tables must remain local.
