"""Breadth-first functional ledger; no device access or production encoder."""
import json
from collections import Counter
from pathlib import Path
from function_names import SETTINGS, EXTRA_ROUTES
from service_names import NAMES
from service_native_names import NATIVE_NAMES
from short_names import ROUTES, SERVICES

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'requirements/package-runs/P0089'
P88 = ROOT / 'requirements/package-runs/P0088'

# Public names are deliberately separate from native-confirmed roles.
PUBLIC = {
'01': 'Läser styrenhetens tid.',
'02': 'Rapporterar avfrostning och termostatstatus.',
'03': 'Rapporterar felkoder och zonernas arbetsstatus.',
'05': 'Rapporterar värmekälla och varmvattenproduktionens status.',
'09': 'Läser temperaturbörvärden och temperaturgränser för zoner och varmvatten.',
'0d': 'Läser framledning och retur separat för zon 1 och zon 2.',
'0e': 'Läser extern pannas framledning och retur.',
'0f': 'Läser ytterligare temperaturgivare; givarnas identitet är modellberoende.',
'10': 'Rapporterar termostaternas värmebehov.',
'11': 'Rapporterar DIP-konfiguration och därmed möjliga systemegenskaper.',
'13': 'Rapporterar kompressordrift och drifttid.',
'16': 'Rapporterar ytterligare vattenpumpars status.',
'29': 'Rapporterar värme/kyla och zonernas temperaturbörvärden.',
'a1': 'Läser förbrukad energi uppdelad på värme, kyla och varmvatten.',
'a2': 'Läser producerad energi uppdelad på värme, kyla och varmvatten.',
}
NATIVE = {
'41.32': 'Begär driftläge och temperaturbörvärden, inklusive fast framledning.',
'41.34': 'Begär boost, semester, driftspärrar och extern styrning; innehåller även begränsningssignal.',
'41.35': 'Begär zonernas separata temperaturmål för värme/kyla; inte samma väg som fast framledning.',
'41.c8': 'Styr en kategoribaserad session för överföring och tillämpning av inställningar.',
'42.04': 'Rapporterar kompressorfrekvens och ytterligare driftstatus, inklusive flera enheter.',
'42.07': 'Rapporterar förbrukad/producerad effekt och en ökande förbrukningsräknare.',
'42.0b': 'Rapporterar rumstemperaturer och andra valda temperaturkällor.',
'42.0c': 'Rapporterar primär framledning, retur och varmvatten samt ytterligare temperaturfält.',
'42.14': 'Rapporterar ingångs-/tillskottsstatus och primärt vattenflöde.',
'42.15': 'Rapporterar pumpar, ventiler och andra aktuatorers driftstatus.',
'42.26': 'Rapporterar valda driftlägen och temperaturmål.',
'42.28': 'Rapporterar boost, semester, driftspärrar och extern styrstatus.',
'42.17': 'Rapporterar givarövervakning, bland annat primär framledning/retur och zongivare; inte själva temperaturerna.',
'42.18': 'Rapporterar ytterligare övervakningsstatus, inklusive rumsgivare; flera delsignaler återstår att namnge.',
'42.a3': 'Förmedlar servicefrågor och deras typade resultat; en gateway med många underkoder.',
'42.c8': 'Rapporterar inställningssessionens acceptans, upptagenstatus eller avvisning; inget tillämpningskvitto.',
'frame.5b': 'Läser information om styrenhet/konfiguration genom C9 i ramtyp 5B.',
}
UNKNOWN = {
'06': 'Rapporterar fyra sammansatta värden; deras funktion är ännu okänd.',
'17': 'Rapporterar interna statusfält; utrustningen eller funktionen de beskriver är ännu okänd.',
'18': 'Rapporterar interna statusfält; utrustningen eller funktionen de beskriver är ännu okänd.',
'19': 'Rapporterar interna statusfält; utrustningen eller funktionen de beskriver är ännu okänd.',
'1a': 'Rapporterar sex värden från samma hjälpfunktion; fysisk betydelse ännu okänd.',
'1b': 'Rapporterar ett internt statusvärde; fysisk betydelse ännu okänd.',
'20': 'Svarspackaren sätter endast svarshuvud och kommando; dataområdets betydelse är okänd.',
}

def build():
    source = json.loads((P88 / 'command-port-matrix.json').read_text())
    rows = []
    for src in source['rows']:
        if src['path'] != 'uart2':
            continue
        key = src['id'].removeprefix('uart2.')
        wire = src['wire']
        opcode = wire.get('opcode', '')
        state, meaning = 'okänd', 'Funktionen återstår att identifiera.'
        refs = ['P0088/command-port-matrix.json#' + src['id']]
        if key in EXTRA_ROUTES:
            name, state, proof, caveat = EXTRA_ROUTES[key]
            meaning = name + '. ' + caveat
            refs += [proof]
        elif key in NATIVE:
            state, meaning = 'identifierad', NATIVE[key]
            refs += src['evidence']
            if key in ('42.17', '42.18'):
                state = 'namngiven del'
                refs += ['A5C86/A5D3A→A4410; AE2CC sensor failure selection; OCH722A request567']
        elif key.startswith('42.') and opcode in PUBLIC:
            state, meaning = 'trolig', PUBLIC[opcode]
            refs += ['F1p Process0x' + opcode.upper() + '; pinned in P0089/provenance.json']
        elif opcode and 0x50 <= int(opcode, 16) <= 0x7e:
            state = 'familj känd'
            action = 'Tar emot' if key.startswith('41.') else 'Lämnar ut'
            meaning = f'{action} inställningsblock {opcode.upper()}; vilka inställningar återstår att namnge.'
            if opcode in SETTINGS:
                name, state, proof, caveat = SETTINGS[opcode]
                meaning = action + ' ' + name[0].lower() + name[1:] + '. ' + caveat
                refs += [proof]
        elif key.startswith('42.') and opcode in ('1c', '1d', '1e', '1f', '27'):
            state = 'platshållare'
            meaning = 'Packar uttryckliga nollvärden i sina datafält i referensfirmwaren; ingen användbar mätfunktion där.'
            refs += ['FTC20.01 packer ' + ','.join(src['handlers']), 'A4CD2 zero helper; private instructions.tsv']
        elif key.startswith('42.') and opcode in UNKNOWN:
            meaning = UNKNOWN[opcode]
        elif key == '41.33':
            meaning = 'Mottas som separat styrhändelse, men ingen verksam konsument har hittats i den avgränsade analysen.'
        elif key.startswith('frame.5c') or key.startswith('frame.5d'):
            meaning = 'Separat CC-ramfamilj; användningsområde ännu okänt.'
        elif key.startswith('frame.02'):
            meaning = 'Alternativ ramtyp 02; dess roll i sessionen återstår att identifiera.'
        rows.append(dict(id=src['id'], wire=wire, port='CN105 / UART2', status=state,
                         function=meaning, name=(SETTINGS[opcode][0] if opcode in SETTINGS and key[:3] in ('41.', '42.') else EXTRA_ROUTES[key][0] if key in EXTRA_ROUTES else meaning.split(';')[0].rstrip('.')), evidence=refs, handlers=src['handlers']))
    rows.append(dict(id='uart2.frame.5a', wire={'frame':'FC','type':'5a','direction':'RX→TX'},
                     port='CN105 / UART2', status='identifierad',
                     name='Anslutning till CN105', function='Etablerar protokollanslutning; separat ramtyp, inte GET/SET-underkommando 5A.',
                     evidence=['P0088/structural-inventory.json: uart2.rx descriptor9 at894BB',
                               'A50F2', 'procon/modular/firmware/src/cn105.c CONNECT'], handlers=['a50f2']))
    for row in rows:
        row['name'] = ROUTES.get(row['id'].removeprefix('uart2.'), row['name'])
    rows.sort(key=lambda r:r['id'])
    services = []
    catalog = json.loads((P88 / 'command-catalog.json').read_text())
    local = {r['code']['selector']: r for r in catalog['services'] if 'selector' in r['code'] and r['id'].startswith('service.local.')}
    for code in sorted(set(NAMES) | {n for n in local if n < 700}):
        item = local.get(code)
        services.append(dict(code_decimal=code, name=NAMES.get(code, NATIVE_NAMES.get(code, ('Funktionen ännu inte namngiven',))[0]),
            naming_status='manualnamn' if code in NAMES else NATIVE_NAMES.get(code, ('','okänd'))[1],
            routing='CN105 avvisar denna kod' if code == 200 else ('lokal FTC-gren belagd; yttre villkor kvarstår' if item else 'manualkod; native A3-rutt inte individuellt kvalificerad här'),
            side_effect='Ändrar serviceväljare och köar sändning; inte mätfråga' if 350 <= code <= 363 else 'Nollställning; inte mätfråga' if code in (200,340,341,342,343,344,532) else (item['effect'] if item else 'Inte individuellt kvalificerad'),
            evidence=(['OCH722A section8-6 pp30–32; pinned local text'] if code in NAMES else []) + ([NATIVE_NAMES[code][2]] if code in NATIVE_NAMES else []) + (item['evidence'] if item else [])))

    for row in services:
        row['description'] = row['name']
        row['name'] = SERVICES.get(row['code_decimal'], row['name'])

    return dict(scope='FTC20.01: 141 previously catalogued routes plus connection primitive; not universal CN105 coverage',
                status='PARTIAL', physical_tests=0, services=services, counts=dict(sorted(Counter(r['status'] for r in rows).items())),
                counting='Routes, not independent features; paired settings reads/writes and A3 subcodes must not be added as equivalent units.',
                public_reference_pin='F1p 7687d11e8f4ec23de13f2c95bcdf76ebe9daebb5', rows=rows)

def render(data):
    lines = ['# CN105 — vad kommandona gör', '',
             'Bredd först enligt användarens prioritering. Funktionen ska få ett begripligt namn före fortsatt fält-, timing- och regulatoranalys.', '',
             'Detta är en första funktionsöversikt, inte en färdig kartläggning. 141 befintliga vägar plus anslutningsramen 5A. Läsning och skrivning räknas separat; A3-underkoder räknas inte som nya ramkommandon.', '',
             '**Identifierad** avser övergripande roll, inte att alla fält är förstådda. **Trolig** är en arbetshypotes från externa referenser eller en kombination av native dataflöde, standardvärden och manual. **Namngiven del** betyder ett blandat paket där bara vissa funktioner har namn. **Familj känd** betyder att inställningsöverföringen är känd men innehållet saknar funktionsnamn. **Platshållare** gäller bara referensfirmwarens skrivna datafält.', '',
             'Räkning: ' + '; '.join(f'{k}: {v}' for k,v in data['counts'].items()) + '.', '',
             'Alla rader gäller CN105/UART2. FC41 = skrivbegäran, FC42 = läsbegäran. Exempelvis FC42/5A och ramtyp FC5A är olika saker. Inga fysiska tester har gjorts i denna genomgång.', '',
             '| Kod/väg | Namn | Beskrivning | Bedömning |', '|---|---|---|---|']
    lines += [f"| {r['id'].removeprefix('uart2.')} | {r['name']} | {r['function']} | {r['status']} |" for r in data['rows']]
    lines += ['', '## Nästa varv — fortfarande bredd', '',
              '1. Bekräfta preliminära SD-formatkopplingar och namnge återstående delar i blandade block. Behandla läs- och skrivparet tillsammans; börja inte kvalificera varje byte.',
              '2. Precisera överordnad avsikt för SET33 och ramfamiljerna 5C/5D/02; GET1B är nu flödesövervakning.',
              '3. Bekräfta de externa funktionsnamnen mot rätt firmware/modell. Särskilt 0F får inte likställas med Geodans brinegivare utan belägg.',
              '4. Ge A3-underkoderna en separat funktionslista med status per kod, utan att åter blanda ihop kodantal och antal ramkommandon.',
              '5. Först därefter fördjupa de funktioner som behövs för effektstyrning.', '',
              'Maskinläsbara källhänvisningar och packaradresser finns i cn105-function-overview.json. Tidigare djupanalys är bevarad men styr inte längre arbetsordningen.', '']
    lines += ['## A3-underkoder — vad funktionen heter', '',
              'Koderna nedan är decimala. Manualnamn betyder dokumenterad funktion i Geodan-manualen, inte verifierat svar över vår CN105-väg. Underkort och FTC skiljs i beskrivningen. Kod200 avvisas av CN105; interna klasser och intervall räknas inte som funktioner.', '',
              '| Kod | Funktionsnamn | Grund |', '|---|---|---|']
    lines += [f"| {r['code_decimal']} | {r['name']} | {r['naming_status']} |" for r in data['services']]
    lines += ['', 'A3-namn och fysiskt tillgängliga värden är separata saker. Ruttvillkor och kända sidoeffekter finns i JSON-listan. Manualens fläktnamn53/122 är bevarade uttryckligen och har inte gissats om till brinefunktioner.', '']
    return '\n'.join(lines)

if __name__ == '__main__':
    data = build()
    (OUT / 'cn105-function-overview.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    (OUT / 'cn105-function-overview.md').write_text(render(data))
    print(json.dumps(data['counts'], ensure_ascii=False))
