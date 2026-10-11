"""Names correlated with Mitsubishi FTC6 SD Tool 1.01 serializers.

File offsets identify the purpose, not proof of physical execution through CN105.
See sd-tool-correlation.md for category, bank and version limitations.
"""
# command: name, enum, offsets, packer, strength
ROWS = {
'57': ('Årsperiod för veckoprogram 2', 'SD_Sch_Pos', [105], 'a77b8', 'trolig'),
'59': ('Semesterläge: aktivering samt start- och slutdatum', 'SD_Hol_Pos', [0,3,6], 'a7816', 'trolig'),
'5c': ('Displayens språk, temperaturenhet och temperaturvisning', 'SD_Is_Pos', [0,3,6], 'a7938', 'trolig'),
'5d': ('Kontakttelefon som visas på manöverpanelen', 'SD_Is_Pos', [9,12,15,18], 'a7984', 'trolig'),
'5e': ('Tidsformat, fjärrkontrollernas zontilldelning och rumsgivarval', 'SD_Is_Pos', [21,24,27,30], 'a79e2', 'trolig'),
'5f': ('Tidsschema för val av rumsgivare per zon', 'SD_Is_Pos', list(range(33,63,3)), 'a7a3a', 'trolig'),
'6e': ('Säsongsperioder för elprisschemat', 'SD_SV_Pos', [165,168], 'a8138', 'trolig'),
'74': ('Veckoschema för elpris i tre säsonger', 'SD_SV2_Pos', [], 'a8402', 'trolig'),
'75': ('Golvtorkning: start-/sluttemperatur, maxtemperatur, hålltid och uppsteg', 'SD_SV2_Pos', [315,318,321,324], 'a8a20', 'trolig'),
'76': ('Golvtorkningens stegintervall/nedsteg och externa ingångar IN4/IN5', 'SD_SV2_Pos', [327,330,333,336], 'a8a90', 'namngiven del'),
'7d': ('Begränsning av eltillskott och sommarlägets temperatur-/tidsgränser', 'SD_SV2_Pos', [411,414,417,420], 'a8d78', 'namngiven del'),
'7e': ('Sommarlägets tvångsstarttemperatur och schema/nivå för tyst drift', 'SD_SV2_Pos', [423,426,429,432], 'a8dda', 'trolig'),
'73': ('Flödessensorns maxvärde, varmvatten-tillskott och Normal/Fast-rumsreglering', 'SD_SV_Pos', [255,258,261], 'a8378', 'identifierad'),
'77': ('Smart-grid-temperaturbidrag, termo-ON-utgång och varmvattenåterladdning', 'SD_SV2_Pos', [339,342,345,348], 'a8afe', 'identifierad'),
'78': ('Variabelt vattenflöde och analogutgångens styrning, intervall och effekt', 'SD_SV2_Pos', [351,354,357,360], 'a8b6c', 'identifierad'),
'79': ('Pump 4:s energibidrag, värmepumpens pumpnivå, analogprioritet och minflöde', 'SD_SV2_Pos', [363,366,369,372], 'a8bcc', 'identifierad'),
'7a': ('Maxflöde, hybridhysteres, buffertgivarkorrigering och smart-grid-värmeval', 'SD_SV2_Pos', [375,378,381,384], 'a8c24', 'identifierad'),
'7b': ('Smart-grid-börvärden för rekommenderad/tvingad värme och kyla', 'SD_SV2_Pos', [387,390,393,396], 'a8c92', 'identifierad'),
'7c': ('Periodisk cirkulation för värme/kyla, intervall och smart-grid-kylval', 'SD_SV2_Pos', [399,402,405,408], 'a8d1e', 'identifierad'),
'6c': ('Konfigurerad COP-tabell, punkter 1–6', 'SD_SV_Pos', list(range(129,147,3)), 'a8008', 'namngiven del'),
'6d': ('Konfigurerad COP-tabell, punkter 7–12', 'SD_SV_Pos', list(range(147,165,3)), 'a80a0', 'namngiven del'),
'6f': ('Elpriser 1–6 för hybridens kostnadsjämförelse', 'SD_SV_Pos', list(range(171,207,6)), 'a8184', 'namngiven del'),
'70': ('Elpriser 7–10 för hybridens kostnadsjämförelse', 'SD_SV_Pos', list(range(207,231,6)), 'a821c', 'namngiven del'),
}

def names():
    result={}
    for code,(name,enum,offsets,packer,status) in ROWS.items():
        proof=f'{packer.upper()}; FTC6 SD Tool1.01 {enum} offsets {offsets}; RCFile.ReadINIT/ReadHOL/ReadSER1/ReadSER2/ReadSCH; sd-tool-correlation.md'
        if status=='trolig':
            caveat='Funktionsnamn från kategorikvalificerad struktur-/offsetmatchning mot SD-verktyget. Peerimplementation och fysisk tillämpning är inte verifierade.'
        else:
            caveat='Namnet stöds av SD-format och native packarens/exportörens gemensamma källor. Gäller konfiguration, inte ett nytt uppmätt värde; fysisk tillämpning ej provad.'
        if code in ('6c','6d'):caveat+=' Detta är INTE live-COP.'
        if code=='77':caveat+=' Ersätter det tidigare alltför breda och missvisande namnet rumsgivarval.'
        if code=='74':caveat+=' Tre säsonger × sju dagar stöds av ReadSER2:s prisparser; tidigare kandidat tyst drift var fel.'
        result[code]=(name,status,proof,caveat)
    return result
