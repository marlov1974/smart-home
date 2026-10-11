# P0089 – handoff till Procon (inga produktionsändringar)

Granskad källa är pinnad i provenance.json. control.c gör redan rätt för target-only:FLOW fyller p6 med current.mode. MODE_FLOW använder0x88 och mode1. Kvittens61 behandlas som hint och följs av GET. Dessa är **inte nya buggar** och ska inte skrivas om som sådana.

Nya möjligheter: explicit begäran om fjärrägande samt fem valbara spärrar med GET28-ägande/statusverifiering; separatSET35-rumsbörvärde; GET05:s valda interna gränsnivå. Inget av detta är ett nu aktiverat API. SET34 p13 är inte kvalificerat för termisk kW-/Hz-styrning.

Konkreta ändringsbehov för ett senare paket:

1. Common/API: en typad transaktion med frame-type, tillåtna fält och owner; API600:s zero-parameterGET räcker inte till5B/C9 eller sessionsfrågor. Ingen fri raw-write-allowlist.
2. Service: separera pendingpolls från transportfel; bevara format och selector; klassificera cacheålder som okänd tills rearm är kvalificerad. Current format0 äter tioförsöksbudgeten och format3/4/7 blir failures.
3. Drift: egen GET05-p5-kodning, GET28-p10ägande och råa hjälptillstånd. Ingen råkod till kW-konvertering.
4. Mode: kontrollera vald effekt/spärr via GET28 och native tillstånd; bekvämt p10-event är inte ett ovillkorligt modebyte. Zonlägen kan kopplas genom860CC. Inga settingsapply förrän alla grannar och peerclose är kvalificerade.

Uppmätt release-p81 (pinnad build-manifest sizes.json; fulla slotbinärer hashverifierade, FF-utfyllnad efter used verifierad): BL2 6584/8192, Common4280/12288, Dispatcher672/4096, Mode12280/12288, Drift2736/4096, Service1360/4096, DebugCommand72/4096, DebugTelemetry208/4096 byte. Mode har bara8 byte ledigt. RAM used/reserved:856/4096,216/2048,8/256,992/4096,616/2048,160/1024,0/256,0/256. Framtida kod måste flyttas/omfördelas eller budgeteras; ingen ny footprint är uppmätt eftersom firmware inte byggts/ändrats.
