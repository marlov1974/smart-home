# P0074 review — WARN

Source synchronized at687abf6; destination main be4f02e4b31c09eed5073a151925361b4fd2bad8, local staged export tree matches destination tree36fd2a4. Use a separate clean private checkout; preserve preceding uncommitted P0072 live evidence in its original checkout.

Deliver a standalone normative compatibility profile, not a claim that all board facts are measured. STM32L433 marking, exact density, bootloader validation/erase behavior, electrical levels, LED polarity and watchdog inheritance/window remain unresolved. Completion permits explicit unknowns. Do not invent controls: P0072 is FC04-only and has no SET/ack/lease. No device access/flash or visibility change in P0074.

Plan: consolidate hardware facts into evidence-tagged recipes; specify complete current wire API; integrate P0073 catalogs; publish golden vectors and machine-readable platform metadata; review all nine independence questions using docs only. Verify CRC/checksum/links/spec consistency with an independent stdlib checker and hosted CI. Preserve firmware source unchanged.
