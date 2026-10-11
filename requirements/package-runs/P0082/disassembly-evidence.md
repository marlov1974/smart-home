# P0082 disassembly evidence

Confirmed byte/decoder facts: reset target D5540 starts with stack-pointer setup (ISP=4FD6, USP=4CD6), SB=0400 and INTB=FFD00, followed by initialization and calls. D5662 decodes REIT. This is coherent M16C/60 startup, not arbitrary high decode density alone.

Official sources: [M16C/60 instruction manual](https://www.renesas.com/en/document/mah/m16c60-m16c20-m16ctiny-series-software-manual), printed pp. 209/219/223 for NOP/REIT/RTS; [M16C/64A hardware manual](https://www.renesas.com/en/document/mah/m16c64a-group-users-manual-hardware); [M16C/65 hardware manual](https://www.renesas.com/en/document/mah/m16c65-group-users-manual-hardware).

Two fresh imports with direct-flow assistance produced exactly the same 57,966 instruction rows and 1,576 inferred functions. SHA-256: instructions `14e1144e3ac6ebba44ca91d5692bfa12fbd023349aab753b099a97bbf7843255`; functions `c26aefd8c0c245c264e79849771d3112aaca16ef56b1e3a29aced02a0119bf3d`; references `1b69b0b6085c8944d6ef33d0f0a31496a28c4e19287b7d2cf9383e831ca00081`. These counts measure the analysis, not true total functions. Later table-seeded analysis adds coverage.

## Service dispatcher: strong hypothesis with instruction evidence

Function 8C0B4 compares a 16-bit selector against service-like codes. Call sites include 8BAB9, 8BBD6, 8BF6B, CEC8A. Shared reply-copy tail is 8D346; it copies three bytes via D4D0C. Address-only case map is in `service-dispatch-candidates.json`. Wire routing to CN105 is not yet proven.

| Selector | Handler | Observed implementation |
|---|---|---|
| 190 | 8C6CE | format 1, reads ROM 80001 then 80000 |
| 191 | 8C6E0 | format 1, reads ROM 80003 then 80002 |
| 506 | 8C8FE | format 2, signed RAM word 0664 divided by 100 |
| 511 | 8C95D | format 2, signed RAM word 0662 divided by 100 |
| 540 | 8CC6E | format 2, unsigned RAM word 322E divided by 100 |
| 550 | 8CC81 | format 3, byte from 39DE plus result of call A22FC |
| 340 | 8C6F2 | writes 1 to RAM 3ADC and returns format 7 |

Minimal example at 8C960/8C964/8C966: `MOV.w 0x662,R0`; `EXTS.w R0`; `DIV.w #0x64`. These are static observations in this image. P0081 supplies the independent display labels for 506/511/540 and format-3 observation for 550. Code 340 reinforces why service-code scans exclude mutating selectors. No write was executed.

## Setting-name use

Table starts at 87620, stride 64, 17 names. 87660=6_HW.DAT, 876A0=6_AC.DAT, 878A0=6_SER1.DAT, 878E0=6_SER2.DAT. At C96E6, selector 4934 is bounded below 17, shifted left six at C9708 and used by LDE.b at C970D to read 87620+offset. The routine copies 64 bytes to 469C+6 then calls the function pointer at 493D. This establishes indexed filename use, not file-field semantics.

Route to that routine is supported by C9461's 21-byte descriptor stride, table base 87A60, copy to 4930 and indirect calls at C948B/C948F/C9493 using fields +5/+9/+17. Rows containing C96E6 were seeded only after verifying that structure. This is not an arbitrary pointer scan.

The final table-assisted script was also run on two fresh imports. All four outputs match exactly; final counts and hashes are in `verification.json`. ID-file address/value pairs independently match image bytes.
