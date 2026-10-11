# Functional matrix and manual parity backlog

R/W mean externally observable read/report and request/write, respectively; they do not authorize actuation. P = proven static route, S = session/sequence incomplete, U = untraced. Unknown does not mean unsupported. Each action is separate from physical connector assignment.

| Action | CN105 R | CN105 W | UART6 R | UART6 W | UART0 R | UART0 W | UART1 R | UART1 W | D R | D W |
|---|---|---|---|---|---|---|---|---|---|---|
| Actual compressor Hz | P GET04 | U | U | U | U | U | U | U | U | U |
| Requested compressor Hz | P A3/17 forwarded | U | U | U | U | U | U | U | S shared services | U |
| Brine inlet temperature | P A3/27 forwarded | U | U | U | U | U | U | U | S shared services | U |
| Brine outlet temperature | P A3/28 forwarded | U | U | U | U | U | U | U | S shared services | U |
| Brine pump level | P A3/18 forwarded | U | U | U | U | U | U | U | S shared services | U |
| Brine pump RPM | P A3/19 forwarded | U | U | U | U | U | U | U | S shared services | U |
| Frequency limitation/state | P A3/52 forwarded | U | U | U | U | U | U | U | S shared services | U |
| Flow temperature | P GET0B/A3/511 | U | U | U | U | U | P12/00 bytes62–63 | U | S services | U |
| Return temperature | P GET0B/A3/506 | U | U | U | U | U | P12/00 bytes64–65 | U | S services | U |
| Primary water flow | P GET14/A3/540 | U | U | U | U | U | P12/01 bytes61–62 | U | S services | U |
| Configured heating pump level | S GET79 p7 | S SET79 whole block | U | U | S SER imports | S SER file | P near read20.01 | U | S settings | S settings |
| Configured DHW pump level | S GET65 p10 | S SET65 whole block | U | U | S SER imports | S SER file | P near read20.01 | U | S settings | S settings |
| Eight wireless room temperatures | U full channels | U | U | P48..4B peer reports | U | U | P near read20.01 | U | U | U |
| Zone selected room target | P GET09 | P SET32 flags | P reply aggregate | P49 p1/mode/zone | S AC file | S AC file | P near read20.01 | U | S shared setters | S shared setters |
| DHW boost | P GET28 | P SET34 | P p5 | P4A p9 | U | U | P12/00 | U | S shared state | S shared state |
| Holiday enable | P GET28 | P SET34 | P p6 | P4B p9 | S HOL file | S HOL file | P12/00 | U | S shared state | S shared state |
| Live consumed/produced power | P GET07 raw, units unvalidated | U | U | U | U | U | U | U | U | U |
| Energy running counters | P A3/520..531; side effects | U | U | U | U | U | P near memory, uncalibrated | U | S shared services | U |
| Energy snapshot/reset | P historical GETA1/A2 | S A3/532 mutates | U | U | U | U | U | U | S shared services | S shared services |
| Diagnostic traffic log | U | U | U | U | P file protocol, distinct log | P dated log writer | P F0 drains | U | U | U |
| Near16 diagnostic memory | U | U | U | U | U | U | P low1 aliases16-bit | U | U | U |
| Metadata/about | P5B/C9 | U | U | U | U | U | P12/00 | U | U | U |

## Source-peer and job functions

Directions below are relative to FTC. They describe the traced software link, not a qualified CN3C pinout or a new Procon command.

| Action | FTC receives | FTC sends / changes | Qualification |
|---|---|---|---|
| Forwarded service result | Type1D, selector10 bits, format3 bits, raw16 | Shared class1 A3 cache updated | No selector-equality check in CECFA; outer gates remain |
| Selected temperature target | U | Descriptor82C2A byte1 from39EF | Half-degree quantization; active profile must be established |
| Selected temperature feedback | U | Descriptor82C2A byte3 from39F1 | Half-degree quantization; heating/DHW selection inBA962 |
| Return temperature | U | Descriptor82C2A byte2 low6 from39F3 | Whole-degree encoding, range0..60 |
| Primary flow feedback | U | Descriptor82C2A byte4 from39F5 | Feature gate and nonlinear encoding; source-outgoing.md |
| A3 job polling | Cached status viaCN105 | Same forwarded selector normally preserves job | Pending differs from failed transport; a new measurement needs rearming |
| A3 job cancellation | Non-A3 internal command can clear ownership | Falling0402 sets0868; service queue bits cleared | Conditional native path, no live test |
| Settings pending-request announcement | Internal service1005 | State1 format1, category mask and direction | D peer schedule unresolved; not externally callable A3 |
| Settings extended end event | D tag1, selector0 | CF978 consumes completion prerequisite | Full transfer sequence remains incomplete |

## Manual-derived action inventory

Source: Mitsubishi OCH722A printed pages20–23, menu tree; applicable optional functions retained with model qualifier. These are required parity targets, not claims of resolved command mappings. See the first table and atlas for established subsets. UI-local is a hypothesis until screen firmware or a transport proves ownership.

| Group | Individual action | Classification / remaining edge |
|---|---|---|
| DHW | Normal/ECO mode | FTC/menu action; exact per-field route/transaction not yet closed |
| DHW | Maximum tank temperature | FTC/menu action; exact per-field route/transaction not yet closed |
| DHW | Recharge temperature drop | FTC/menu action; exact per-field route/transaction not yet closed |
| DHW | Maximum DHW run time | FTC/menu action; exact per-field route/transaction not yet closed |
| DHW | DHW restriction duration | FTC/menu action; exact per-field route/transaction not yet closed |
| DHW | Forced DHW boost | FTC/menu action; exact per-field route/transaction not yet closed |
| DHW | DHW operating/prohibited/timer permission | FTC/menu action; exact per-field route/transaction not yet closed |
| Hygiene | Enable legionella cycle | FTC/menu action; exact per-field route/transaction not yet closed |
| Hygiene | Legionella target temperature | FTC/menu action; exact per-field route/transaction not yet closed |
| Hygiene | Legionella frequency | FTC/menu action; exact per-field route/transaction not yet closed |
| Hygiene | Legionella start time | FTC/menu action; exact per-field route/transaction not yet closed |
| Hygiene | Legionella maximum runtime | FTC/menu action; exact per-field route/transaction not yet closed |
| Hygiene | Hold duration at maximum temperature | FTC/menu action; exact per-field route/transaction not yet closed |
| Heating | Zone1 room/fixed-flow/curve mode | FTC/menu action; exact per-field route/transaction not yet closed |
| Heating | Zone2 room/fixed-flow/curve mode | FTC/menu action; exact per-field route/transaction not yet closed |
| Heating | Zone1 room target | FTC/menu action; exact per-field route/transaction not yet closed |
| Heating | Zone2 room target | FTC/menu action; exact per-field route/transaction not yet closed |
| Heating | Zone1 flow target | FTC/menu action; exact per-field route/transaction not yet closed |
| Heating | Zone2 flow target | FTC/menu action; exact per-field route/transaction not yet closed |
| Heating | Zone1 curve points | FTC/menu action; exact per-field route/transaction not yet closed |
| Heating | Zone2 curve points | FTC/menu action; exact per-field route/transaction not yet closed |
| Heating | Zone1 curve adjustment | FTC/menu action; exact per-field route/transaction not yet closed |
| Heating | Zone2 curve adjustment | FTC/menu action; exact per-field route/transaction not yet closed |
| Heating | Heating operating/prohibited/timer permission | FTC/menu action; exact per-field route/transaction not yet closed |
| Schedule | Schedule1/2 selection | FTC/menu action; exact per-field route/transaction not yet closed |
| Schedule | Schedule2 date period | FTC/menu action; exact per-field route/transaction not yet closed |
| Schedule | Zone1 day selection | FTC/menu action; exact per-field route/transaction not yet closed |
| Schedule | Zone1 time intervals | FTC/menu action; exact per-field route/transaction not yet closed |
| Schedule | Zone1 scheduled temperatures | FTC/menu action; exact per-field route/transaction not yet closed |
| Schedule | Zone2 day selection | FTC/menu action; exact per-field route/transaction not yet closed |
| Schedule | Zone2 time intervals | FTC/menu action; exact per-field route/transaction not yet closed |
| Schedule | Zone2 scheduled temperatures | FTC/menu action; exact per-field route/transaction not yet closed |
| Schedule | DHW schedule day selection | FTC/menu action; exact per-field route/transaction not yet closed |
| Schedule | DHW schedule time intervals | FTC/menu action; exact per-field route/transaction not yet closed |
| Schedule | Schedule preview | FTC/menu action; exact per-field route/transaction not yet closed |
| Schedule | Schedule save | FTC/menu action; exact per-field route/transaction not yet closed |
| Holiday | Holiday enable | FTC/menu action; exact per-field route/transaction not yet closed |
| Holiday | Holiday date/time interval | FTC/menu action; exact per-field route/transaction not yet closed |
| Holiday | Holiday DHW permission | FTC/menu action; exact per-field route/transaction not yet closed |
| Holiday | Holiday zone1 heating permission | FTC/menu action; exact per-field route/transaction not yet closed |
| Holiday | Holiday zone2 heating permission | FTC/menu action; exact per-field route/transaction not yet closed |
| Holiday | Holiday zone1 room target | FTC/menu action; exact per-field route/transaction not yet closed |
| Holiday | Holiday zone2 room target | FTC/menu action; exact per-field route/transaction not yet closed |
| Holiday | Holiday zone1 flow target | FTC/menu action; exact per-field route/transaction not yet closed |
| Holiday | Holiday zone2 flow target | FTC/menu action; exact per-field route/transaction not yet closed |
| Initial/UI | Date/time | FTC/menu action; exact per-field route/transaction not yet closed |
| Initial/UI | Language | Screen-local candidate; wire/native owner untraced |
| Initial/UI | Summer time | Screen-local candidate; wire/native owner untraced |
| Initial/UI | Temperature display selection | Screen-local candidate; wire/native owner untraced |
| Initial/UI | Contact telephone number | Screen-local candidate; wire/native owner untraced |
| Initial/UI | Time display format | Screen-local candidate; wire/native owner untraced |
| Initial/UI | Celsius/Fahrenheit | Screen-local candidate; wire/native owner untraced |
| Initial/UI | Menu lock/unlock | Screen-local candidate; wire/native owner untraced |
| Room controllers | Room controller zone assignment | FTC/menu action; exact per-field route/transaction not yet closed |
| Room controllers | Zone1 sensor choice TH1/MainRC/RC1..8 | FTC/menu action; exact per-field route/transaction not yet closed |
| Room controllers | Zone2 sensor choice TH1/MainRC/RC1..8 | FTC/menu action; exact per-field route/transaction not yet closed |
| Room controllers | Zone1 timed sensor choice | FTC/menu action; exact per-field route/transaction not yet closed |
| Room controllers | Zone2 timed sensor choice | FTC/menu action; exact per-field route/transaction not yet closed |
| Service | Manual pump override | FTC/menu action; exact per-field route/transaction not yet closed |
| Service | Manual valve override | FTC/menu action; exact per-field route/transaction not yet closed |
| Service | Function settings and restart recovery | FTC/menu action; exact per-field route/transaction not yet closed |
| Service | Heat source selection | FTC/menu action; exact per-field route/transaction not yet closed |
| Service | Heating pump level | FTC/menu action; exact per-field route/transaction not yet closed |
| Service | Heat pump flow minimum | FTC/menu action; exact per-field route/transaction not yet closed |
| Service | Heat pump flow maximum | FTC/menu action; exact per-field route/transaction not yet closed |
| Service | Quiet mode | FTC/menu action; exact per-field route/transaction not yet closed |
| Service | Thermo ON output zone assignment | FTC/menu action; exact per-field route/transaction not yet closed |
| Service | Commissioning wizard | FTC/menu action; exact per-field route/transaction not yet closed |
| Service | Running information selector | FTC/menu action; exact per-field route/transaction not yet closed |
| Service | Thermistor display | FTC/menu action; exact per-field route/transaction not yet closed |
| Service | Settings summary | FTC/menu action; exact per-field route/transaction not yet closed |
| Service | Error history | FTC/menu action; exact per-field route/transaction not yet closed |
| Service | Service password | FTC/menu action; exact per-field route/transaction not yet closed |
| Service | FTC manual reset | FTC/menu action; exact per-field route/transaction not yet closed |
| Service | MainRC manual reset | FTC/menu action; exact per-field route/transaction not yet closed |
| Thermistor adjustment | THW1 flow calibration | FTC/menu action; exact per-field route/transaction not yet closed |
| Thermistor adjustment | THW2 return calibration | FTC/menu action; exact per-field route/transaction not yet closed |
| Thermistor adjustment | THW5A tank upper calibration | FTC/menu action; exact per-field route/transaction not yet closed |
| Thermistor adjustment | THW5B tank lower calibration | FTC/menu action; exact per-field route/transaction not yet closed |
| Thermistor adjustment | THW6 zone1 flow calibration | FTC/menu action; exact per-field route/transaction not yet closed |
| Thermistor adjustment | THW7 zone1 return calibration | FTC/menu action; exact per-field route/transaction not yet closed |
| Thermistor adjustment | THW8 zone2 flow calibration | FTC/menu action; exact per-field route/transaction not yet closed |
| Thermistor adjustment | THW9 zone2 return calibration | FTC/menu action; exact per-field route/transaction not yet closed |
| Thermistor adjustment | THW10 mixing tank calibration | FTC/menu action; exact per-field route/transaction not yet closed |
| Thermistor adjustment | THWB1 boiler flow calibration | FTC/menu action; exact per-field route/transaction not yet closed |
| Auxiliary | Pump economy enable | FTC/menu action; exact per-field route/transaction not yet closed |
| Auxiliary | Pump economy off delay | FTC/menu action; exact per-field route/transaction not yet closed |
| Auxiliary | Heating booster enable | FTC/menu action; exact per-field route/transaction not yet closed |
| Auxiliary | Heating booster delay | FTC/menu action; exact per-field route/transaction not yet closed |
| Auxiliary | DHW booster/immersion enable | FTC/menu action; exact per-field route/transaction not yet closed |
| Auxiliary | DHW heater delay | FTC/menu action; exact per-field route/transaction not yet closed |
| Auxiliary | Mixing valve running time | FTC/menu action; exact per-field route/transaction not yet closed |
| Auxiliary | Mixing valve control interval | FTC/menu action; exact per-field route/transaction not yet closed |
| Auxiliary | Flow sensor minimum | FTC/menu action; exact per-field route/transaction not yet closed |
| Auxiliary | Flow sensor maximum | FTC/menu action; exact per-field route/transaction not yet closed |
| Auxiliary | Analog output priority | FTC/menu action; exact per-field route/transaction not yet closed |
| Auxiliary | Analog output interval | FTC/menu action; exact per-field route/transaction not yet closed |
| Native operation | Heating flow lower limit | FTC/menu action; exact per-field route/transaction not yet closed |
| Native operation | Heating flow upper limit | FTC/menu action; exact per-field route/transaction not yet closed |
| Native operation | Room control mode | FTC/menu action; exact per-field route/transaction not yet closed |
| Native operation | Room control interval | FTC/menu action; exact per-field route/transaction not yet closed |
| Native operation | Heat-pump thermo differential enable | FTC/menu action; exact per-field route/transaction not yet closed |
| Native operation | Heat-pump thermo differential lower | FTC/menu action; exact per-field route/transaction not yet closed |
| Native operation | Heat-pump thermo differential upper | FTC/menu action; exact per-field route/transaction not yet closed |
| Native operation | Freeze-stat target | FTC/menu action; exact per-field route/transaction not yet closed |
| Native operation | Freeze-stat ambient threshold | FTC/menu action; exact per-field route/transaction not yet closed |
| Native operation | Simultaneous operation enable | FTC/menu action; exact per-field route/transaction not yet closed |
| Native operation | Simultaneous ambient threshold | FTC/menu action; exact per-field route/transaction not yet closed |
| Native operation | Cold-weather enable | FTC/menu action; exact per-field route/transaction not yet closed |
| Native operation | Cold-weather ambient threshold | FTC/menu action; exact per-field route/transaction not yet closed |
| Native operation | Summer mode enable | FTC/menu action; exact per-field route/transaction not yet closed |
| Native operation | Summer heating-on ambient threshold | FTC/menu action; exact per-field route/transaction not yet closed |
| Native operation | Summer heating-off ambient threshold | FTC/menu action; exact per-field route/transaction not yet closed |
| Native operation | Summer heating-on judgement time | FTC/menu action; exact per-field route/transaction not yet closed |
| Native operation | Summer heating-off judgement time | FTC/menu action; exact per-field route/transaction not yet closed |
| Native operation | Forced heating duration | FTC/menu action; exact per-field route/transaction not yet closed |
| Native operation | Water flow control enable | FTC/menu action; exact per-field route/transaction not yet closed |
| Native operation | Pump cycles enable | FTC/menu action; exact per-field route/transaction not yet closed |
| Native operation | Pump cycles interval | FTC/menu action; exact per-field route/transaction not yet closed |
| Boiler/hybrid optional | Hybrid priority ambient/cost/CO2 | Optional applicability; per-field native route untraced |
| Boiler/hybrid optional | Hybrid outdoor threshold | Optional applicability; per-field native route untraced |
| Boiler/hybrid optional | Hybrid electricity price | Optional applicability; per-field native route untraced |
| Boiler/hybrid optional | Hybrid boiler price | Optional applicability; per-field native route untraced |
| Boiler/hybrid optional | Hybrid electricity emissions | Optional applicability; per-field native route untraced |
| Boiler/hybrid optional | Hybrid boiler emissions | Optional applicability; per-field native route untraced |
| Boiler/hybrid optional | Hybrid boiler efficiency | Optional applicability; per-field native route untraced |
| Boiler/hybrid optional | Hybrid heat-pump capacity | Optional applicability; per-field native route untraced |
| Boiler/hybrid optional | Hybrid heat-source schedule | Optional applicability; per-field native route untraced |
| Boiler/hybrid optional | Hybrid intelligent enable | Optional applicability; per-field native route untraced |
| Boiler/hybrid optional | Hybrid minimum temperature | Optional applicability; per-field native route untraced |
| Floor dry | Floor dry enable | FTC/menu action; exact per-field route/transaction not yet closed |
| Floor dry | Start/finish temperature | FTC/menu action; exact per-field route/transaction not yet closed |
| Floor dry | Maximum temperature | FTC/menu action; exact per-field route/transaction not yet closed |
| Floor dry | Temperature increase step | FTC/menu action; exact per-field route/transaction not yet closed |
| Floor dry | Temperature decrease step | FTC/menu action; exact per-field route/transaction not yet closed |
| Floor dry | Maximum temperature duration | FTC/menu action; exact per-field route/transaction not yet closed |
| Floor dry | Increase interval | FTC/menu action; exact per-field route/transaction not yet closed |
| Floor dry | Decrease interval | FTC/menu action; exact per-field route/transaction not yet closed |
| Energy | Consumed energy by period and mode | FTC/menu action; exact per-field route/transaction not yet closed |
| Energy | Delivered energy by period and mode | FTC/menu action; exact per-field route/transaction not yet closed |
| Energy | Booster1 capacity | FTC/menu action; exact per-field route/transaction not yet closed |
| Energy | Booster2 capacity | FTC/menu action; exact per-field route/transaction not yet closed |
| Energy | Immersion heater capacity | FTC/menu action; exact per-field route/transaction not yet closed |
| Energy | Water pump1 input power | FTC/menu action; exact per-field route/transaction not yet closed |
| Energy | Water pump2 input power | FTC/menu action; exact per-field route/transaction not yet closed |
| Energy | Water pump3 input power | FTC/menu action; exact per-field route/transaction not yet closed |
| Energy | Water pump4 input power | FTC/menu action; exact per-field route/transaction not yet closed |
| Energy | Electric meter configuration | FTC/menu action; exact per-field route/transaction not yet closed |
| Energy | Heat meter configuration | FTC/menu action; exact per-field route/transaction not yet closed |
| Energy | Delivered energy adjustment | FTC/menu action; exact per-field route/transaction not yet closed |
| External inputs | Demand control IN4 heat-source/boiler choice | FTC/menu action; exact per-field route/transaction not yet closed |
| External inputs | Outdoor thermostat IN5 heater/boiler choice | FTC/menu action; exact per-field route/transaction not yet closed |
| External inputs | Smart grid DHW target | FTC/menu action; exact per-field route/transaction not yet closed |
| External inputs | Smart grid heating enable | FTC/menu action; exact per-field route/transaction not yet closed |
| External inputs | Smart grid heating target | FTC/menu action; exact per-field route/transaction not yet closed |
| SD | Read selected settings SD→MainRC | FTC/menu action; exact per-field route/transaction not yet closed |
| SD | Write selected settings MainRC→SD | FTC/menu action; exact per-field route/transaction not yet closed |

The inventory does not certify pressure/current/voltage channels absent: source-controller analog values and diagnostic arrays need further name/unit tracing. Pairing identity and battery status remain unlabeled; indexed room channels are not proof of radio pairing control. Full semantic parity is therefore PARTIAL.
