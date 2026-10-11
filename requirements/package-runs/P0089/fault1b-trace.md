# GET1B — övervakning av tillåtet vattenflöde

Tidigare direktreferenssökning hittade bara A5EFC→49B6. En sökning av själva binären hittade pekaren49B6 i descriptor857E2: rad7 i85702, stride32. Tabellen binder till callbacktabell882FC. Denna indirekta väg är den saknade producenten.

ACB52 läser descriptorerna, väljer callback efter tillstånd och skriver dess returvärde till descriptorens statuspekare. För rad7 är utvärderingen D2C00 och statusreturen D2D5A. ACC4E konsumerar samma status i den gemensamma felövervakningen.

D2C00 jämför322E (primärflöde) med100×07E8 (minflöde) och100×07E9 (maxflöde). Separata tidsfilter används för lågt flöde, högt flöde och återgång till normalt intervall. Vid kvalificerad avvikelse blir49B7=3; efter kvalificerad normalisering återställs det till0. D2D5A returnerar3 vid avvikelse, annars0. ACB52 skriver detta indirekt till49B6. A5EFC normaliserar via A4410 och bygger GET1B-svaret.

```text
if övervakningen är spärrad:
    återställ övervakning via D2D6A
elif avvikelse redan registrerad:
    om minflöde <= flöde <= maxflöde under återställningsfiltret:
        avvikelse = 0
else:
    om för lågt eller för högt flöde varar tillräckligt länge:
        avvikelse = 3
status49B6 = callback_status(avvikelse)
GET1B = A4410(status49B6)
```

Namnet är därmed **status för övervakning av värmepumpens tillåtna vattenflöde**, inte flödesmätning i l/min. Exakta tidsgränser, spärrvillkor och visad felkod ligger utanför detta namngivningssteg. Ingen fysisk testning. Nya privata Ghidra-utdrag och descriptorbytes har hash i fault1b-trace.json. P88-exporten är oförändrad.
