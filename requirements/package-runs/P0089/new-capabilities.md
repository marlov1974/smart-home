# P0089 – vad Procon kan få ut av denna etapp

Nya kvalificerade länkar, ännu inte installerade:

- Fem individuella värme-/kyl-/varmvattenspärrar kan modelleras korrekt med fjärrägande och GET28-återläsning. Tidigare saknades länken39A6→vald399A.
- Begäran om fjärrägande är en händelse som FTC kan neka/återkalla. GET28 p10 skiljer begäran från accepterat ägande. Watchdog/räknare och peerrelease är verkliga guards.
- SET35 kan skriva separata rumsmål för zon1/2 i uppvärmning eller kylning. Detta är inte fast framledning, och full validering/readback återstår.
- SET34 p13 går in som en övre gräns i en intern min-aggregation; GET05 p5 återger vald, kvantiserad nivå. Enheten/kompressorkopplingen är inte bevisad, så detta är inte en ny effektstyrning i kW.
- GET0B p11 kan avkodas med fastställd avrundning/klamp; rå sensorvaliditet är fortsatt separat.
- Zonlägesändringar kan justera även zon2 via en kompatibilitetstabell. Procon ska observera båda lägena när funktionen senare införs.

Offline levererat: råram-/A3-dekoder, kontrollmodeller, cache-/ägandeobservatör, villkorad settingsobservatör och explicit stopp för ofullständigt bevarande. Ingen ny produktionskod, fysisk capability eller komplett settingssekvens hävdas.14 fält-/kodningskanter är dokumenterade; återstående arbete är i open-questions.md.
