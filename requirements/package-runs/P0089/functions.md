# P0089 function design

- controls.ownership: prior owner, request/release/fault gates -> selected owner; pure model of CE9C8, including invalid owner normalization.
- controls.inhibit_status: local/remote masks and owner -> selected status; preserve previous status for invalid owner.
- controls.counter_step: enabled0/1 -> byte counter and state, invalid preserves; explicit wrap.
- controls.demand_selection: raw p13 staging/override -> selected minimum; no percent/kW claim.
- controls.target35: payload/profile/prior target slots -> separate heating/cooling zone storage, FFFF disabled/ignored.
- codec.frame/parse: explicit FC type/payload, bounded22 bytes and sum check. No implicit production-ready packet planning.
- codec.a3: parse raw format, selector and value without invented scalar meaning; reject maintenance in read planning.
- models.ServiceObserver: explicit owner, pending/cache/freshness/cancelled status, no guessed firmware rearm.
- models.SettingsObserver: explicit synthetic events; preserve applied flag through abort/timeout; block unqualified category apply.
- report.build/render: evidence-backed field catalog,47-block work ledger, route backlog and Swedish readable reports; deterministic outputs and schema checks.

No transport methods, shared helper edits or production changes. Tests tied to branch semantics and artifact conservation.

Added target32 (B9AD0/B9BFE bounded store slice) and coupled_modes (BBE92 table-based requested-mode slice) to test mode context, two-zone routing and profile-dependent coupling. Neither models full selected/effective target publication.

## Revised priority — breadth before depth

User instruction: identify what every CN105 command does before further implementation analysis. `overview.py` conserves the 141 P88 routes and adds the separately evidenced FC5A connection primitive. It distinguishes native function identification, external probable labels, unidentified settings contents, placeholders, and unknown roles. No claim that a known family means a known setting. Next pass names remaining blocks and A3 subfunctions; detailed field qualification is deferred.

Second breadth pass: add curated function_names/service_names data and a conservation test. Reuse existing native assembly and local manufacturer manual; retain hypotheses and unnamed members. Git fetch found no remote divergence; local changes are the immediately preceding authorized P89 continuation, preserved in place. No new package or deployment.


## Fortsättning: följ kommandona till funktionsnamn

Samtliga23 tidigare luckor följda genom native konsumenter eller explicit gräns. Ny extern källa: Mitsubishi FTC6 SD Tool1.01, statisk analys av metadata/läsmetoder och tabeller; filer hålls privat.23 kommandon korrelerade.47/47 inställningsblock har nu minst ett kvalificerat namn, inklusive hypoteser och tomma platser. GET1B:s49B6 följs via descriptor857E2/ACB52 till D2C00:s min-/maxflödesövervakning. Nya privata Ghidra-rötter hålls utanför public repo.33 A3-namn tillagda separat från109 manualnamn.17 A3-koder och fyra protokollvägars överordnade avsikt kvarstår; ingen fullständig funktionell täckning påstås. Se function-naming-progress.md, sd-tool-correlation.md och fault1b-trace.md. Inga liveåtgärder, runtimeändringar eller ändringar i P86–88. P89 publikt27pass/1skip; privat28pass.


Senare A3-fortsättning: se a3-functions.md. Alla17 tidigare luckor har följts vidare;14 fysiska mottagarbetydelser är fortfarande okända. Totalt30 tester: privat30pass, publikt29pass/1skip.


## Sista namnpassage

name_registry.build: läser P89-översikt och P88-atlas, ger separata command/service/field-listor med namn, originalmetadata och osäkerhet. render: skriver namnregister. Testa täckning, unika ID:n, oförändrad osäkerhet och reproducerbarhet. overview.build/render får korta kommandonamn separata från beskrivning; inga protokolländringar.


## Syftesanalys

purpose_fields.ROWS beskriver specifika verifierade övervakningsfält; name_registry.build kopplar via packare+payloadposition och behåller originalmetadata. Extraktion av descriptorbytes och callbackhashar är privat fixture-verifiering. Testerna skyddar fältpositioner och motiverade syften.


## Fortsatt fältsyfte och indirekta tillstånd

Se [field-purpose-findings.md](field-purpose-findings.md) och [field-purpose-audit.md](field-purpose-audit.md). Av965 återstående råa byteförekomster har932 fått syfte eller protokollroll;33 är fortsatt öppna.334 grupper skiljer mätning, konfiguration och protokoll. Detta är inte932 nya funktioner och inte full semantisk täckning. Nya fynd: shuntutgångarnas betydelse, temperaturavvikelse utan Hz-respons, hybridens kostnad/CO2-faktorer, eltillskott/pannans eftergång och nollreturerna iGET1C–1F.

350/351 har nu modellkvalificerad primärmanualkoppling till återställning/pump-down på SUZ; inte verifierat på Geodan. Övriga serviceval och vissa protokollintentioner är fortfarande öppna.39 tester passerar med privata fixtures. Inga liveåtgärder, inga firmwareändringar och inga ändringar iP86–88.
