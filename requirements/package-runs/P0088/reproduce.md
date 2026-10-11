# Offline reproduction

From the repository root, run the synthetic checks without firmware or devices:

```sh
python3 -m unittest discover -s tools/ftc6/p88 -p test_p88.py -v
```

Private image tests require the exact SHA-pinned image and a P83Trace catalog. Set `P88_IMAGE` to the binary path and `P88_CATALOG` to the targeted catalog directory, then repeat the same command. All 21 tests pass with these inputs; the private-image class is skipped without them.

Generate the atlas from those private inputs:

```sh
python3 tools/ftc6/p88/atlas.py "$P88_IMAGE" "$P88_CATALOG" requirements/package-runs/P0088
python3 tools/ftc6/p88/matrix.py
```

The image reader rejects wrong length/hash and out-of-bounds tables. Atlas construction rejects missing core operand references. Private catalog generation follows the P83Seed/P83Trace workflow from P87, using roots from the extracted descriptor callbacks plus the explicitly traced service dispatcher. Full private outputs stay outside the public repository.

For source-link repetition, independently copy the completed P87 baseline project twice. In each copy, seed known roots `9cbd0,9cbf6,9cfd2,9d08c,9c488,9ca40,9cf66` at depth 1 with P83Seed, export them with P83Trace, then run P88SourceSwitch with an output directory. Compare the seven `.asm` files and sixteen branch files byte-for-byte; recorded hashes are in source-extraction.json. Never seed the exploratory interior address 9CB0A. Export 9C660/9C77C separately for the receive/checksum trace.

The smaller offline decoders validate only their documented envelopes and selected fields. They do not reproduce transport timing, device personality, transaction history or the full FTC execution state. No tool here sends traffic or deploys firmware. Full semantic atlas reproduction remains incomplete, matching the package's PARTIAL status.

Additional public consistency check:

```sh
python3 tools/ftc6/p88/verify_artifacts.py requirements/package-runs/P0088
```

Regenerate the source descriptor report from the hash-pinned image and a complete private P83Trace `instructions.tsv` taken after the outgoing switch has been decoded:

```sh
python3 tools/ftc6/p88/source_tx.py "$P88_IMAGE" "$P88_SOURCE_LISTING" requirements/package-runs/P0088/source-tx-descriptors.json
```

It rejects any descriptor lacking a contiguous qualified PUSH/PUSH/JSR caller. Earlier listings taken before switch expansion are intentionally insufficient.

For the continuation comparison, seed/export routines `9a336,9a36a,9a39e,9a3d2,9bc40,9be98,9bf0e,9c002,9c0ee,9c34a,9c39e,9c40e,8b7e2,8bd02,8d36c,8d694,cefa8,cf28a,cf306` in both independent projects. Run `P88SourceSwitch <private-directory> tx` in each. Run `P88A3Completion <private-output-file> <reference-binary>` in each to obtain the complete CECFA CFG; a stale function-body export is insufficient. Compare all43 assembly exports byte-for-byte. Require the explicit success marker and no SCRIPT ERROR; Ghidra process exit zero alone is not success.

Settings continuation repeats17 roots in the two independent projects: `b984a,bb9dc,bbbea,bbfca,bd166,bd296,bd780,cf846,90bd4,bcb0a,bcff4,923bc,cf12e,cf35c,90aba,bc0d8,bc9da`. P83Seed depth1 followed by P83Trace produces the files hashed in settings-transfer-extraction.json. Review923BC using signed-FB-corrected assembly, not its erroneous constant-return C. Atlas generation also regenerates the33-range settings-transfer-map.md.

Persistence continuation: use the roots and first-export groups recorded in `settings-store-extraction.json` with the existing P83Seed/P83Trace flow on two private project copies. Compare each C/assembly file; these are reproducibility checks, not an independent decoder. Run P88A3Completion with output path, reference binary and optional `settings-clock`; omit the third argument to regress the original A3 path. The clock bound ends before unmapped padding. The regular P88 unittest command includes the pure settings-store model.
