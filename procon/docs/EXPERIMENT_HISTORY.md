# Experiment history

- test1: repurposed old query/register paths during brine investigation.
- test2-test5: A3/service-code and timing/retry experiments; early retry interpretations were incomplete.
- test6: useful A3 debugger; exposed response count, status/stop reason and full 16-byte A3 payload. Captured `A3 00 1B 00...`.
- test7: A3 service 19 control.
- test8: A3 service 3 control. Compressor frequency could change while A3 attempts accumulated, proving normal polling continued between A3 visits.
- test9-test12: attempted scheduler locks. Debug lock markers did not execute as expected; internal scheduler assumptions were wrong.
- test13: attempted direct A3 retransmission and misused `0x08010EDC` as raw TX. CN105 communication broke. Superseded.
- test14: attempted passive TX trace. Communication was disturbed and trace magic was not observed. Do not use it as evidence of actual transmitted data.

Decision after test14: stop incremental scheduler patching. Reverse-engineer only enough hardware to create clean replacement firmware. First clean target: Modbus Input Register 0 = 888.
