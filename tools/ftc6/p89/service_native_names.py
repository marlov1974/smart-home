"""Native names kept separate from service-manual labels and SD ItemCode IDs."""
# code: name, classification, evidence
NATIVE_NAMES={
155:('Kompressorns ackumulerade drifttidsräknare (grov del)', 'namngiven del', '8C4BF→14FC; A1448 counts while3A2C=1; interval unit not requalified'),
178:('Primärpumpens återrapporterade signal', 'identifierad', '8C67D→3E9D; same source as GET15; P83 pump-control-trace; not RPM'),
179:('Termo-ON-utgångens status', 'identifierad', '8C68A→49A7; D1C6E/D1CE6 uses07DD, named Thermo ON output by SD_SER2 offset345'),
185:('Förbrukningsberäkningens aktuella värde', 'namngiven del', '8C6A0→CDFD2 selects3216/321A by099B; P86 energy; unit/timebase unqualified'),
186:('Värmeproduktionsberäkningens aktuella värde', 'namngiven del', '8C6B7→CE01E selects3222/3226 by099C; P86 energy; unit/timebase unqualified'),
341:('Nollställ kompressorns grova drifttidsräknare', 'identifierad', '8C6FF→3AE0; A1448 clears3D8C and14FC'),
500:('Rumsbörvärde värme, zon 1', 'identifierad', '8C88C→38DC/100; C979E and SD_HtCl_Pos6'),
501:('Framledningsbörvärde värme, zon 1', 'identifierad', '8C89F→38DE/100; C979E and SD_HtCl_Pos9'),
502:('Rumsbörvärde kyla, zon 1', 'identifierad', '8C8B2→38E2/100; C979E and SD_HtCl_Pos15'),
503:('Framledningsbörvärde kyla, zon 1', 'identifierad', '8C8C5→38E4/100; C979E and SD_HtCl_Pos18'),
516:('Extern pannas returtemperatur', 'namngiven del', '8C9BC→067C/100; A4132→GET0C; THWB2 physical naming remains model-dependent'),
517:('Rumsbörvärde värme, zon 2', 'identifierad', '8C9CF→38EE/100; C979E and SD_HtCl_Pos30'),
518:('Framledningsbörvärde värme, zon 2', 'identifierad', '8C9E2→38F0/100; C979E and SD_HtCl_Pos33'),
519:('Rumsbörvärde kyla, zon 2', 'identifierad', '8C9F5→38F4/100; C979E and SD_HtCl_Pos48'),
532:('Spara och nollställ energiräknarbanken', 'identifierad', '8CC18→CDF46; P86 energy-qualification, not a passive query'),
533:('Framledningsbörvärde kyla, zon 2', 'identifierad', '8CC22→38F6/100; C979E and SD_HtCl_Pos51'),
566:('Extern pannas returtemperatur vid fel', 'namngiven del', '8CF01→3E2F/100; AE1EA copies067C, AE390 restores history'),
570:('Primärpumpens återrapporterade signal vid fel', 'identifierad', '8CF3B→3E2C; AE1EA copies3E9D, AE390 restores history'),
572:('Varmvattentemperatur vid fel', 'identifierad', '8CF56→3E23/100; AE1EA copies0666, AE390 restores history'),
573:('Termo-ON-utgångens status vid fel', 'identifierad', '8CF69→3E1A bit0; AE1EA←3E59; ADD64←49A7'),
574:('Bufferttankstemperatur vid fel', 'namngiven del', '8CF8C→3E3D/100; AE1EA copies0690; GET12 mixing/buffer temperature'),
}
for base,bucket in [(520,'förbrukning varmvatten'),(522,'förbrukning värme'),(524,'förbrukning kyla'),(526,'produktion varmvatten'),(528,'produktion värme'),(530,'produktion kyla')]:
    for low in (0,1):
        NATIVE_NAMES[base+low]=(f'Energiräknare {bucket}, '+('lägre siffror' if low else 'högre siffror'),'trolig','8C0B4→CE0D2; P86 energy-qualification: bucket strong hypothesis, unit unknown; even reads fold counters')

# A3 continuation: semantic boundaries remain explicit for peer-side controls.
NATIVE_NAMES.update({
160: ('FTC modellprofil-ID', 'namngiven del', '8C52B→38BC; 8F142 remaps profile through80FF8; 91948 selects configuration record88E95; model-number dictionary unresolved'),
161: ('FTC DIP-vald hårdvaruvariant', 'namngiven del', '8C538→38BD; 8E3DE extracts3879 bits2..6; 91948 indexes81ADC; CE2A4 selects pump-power table87F9A; exact variant names unresolved'),
536: ('Kondenserings-/mättnadstemperatur från FTC:s givarkanal', 'trolig', '8CC5B→0692 signed/100; 8DDD0:0ADC→80DF2→0692 gated0915/0A8C; A59E4 packs GET0F bytes4..5, matching pinned EcodanDecoder CondensingTemp; not independently validated T63HS/brine'),
350: ('Nollställ serviceväljare för källsidan', 'namngiven del', '8C733 clears39FE/39FF/3A00/3A01 and sets3A76; not proven physical stop or factory reset'),
})
for code in range(351,358):
    NATIVE_NAMES[code]=(f'Välj källsidans serviceläge {code-350} (fysisk funktion okänd)', 'namngiven del',
        f'8C0B4 writes39FE={code-350}, clears39FF/3A00/3A01, sets3A76; A162A sets39CD; descriptor82B34 byte2 bits0..2; peer semantics absent')
for code,field,value,bit in [(358,'39FF',1,4),(359,'39FF',2,4),(360,'3A00',1,0),(361,'3A00',2,0),(362,'3A01',1,2),(363,'3A01',2,2)]:
    NATIVE_NAMES[code]=(f'Källsidans serviceval {field}: värde {value} (fysisk funktion okänd)', 'namngiven del',
        f'8C0B4 writes{field}={value}, clears other two auxiliary selectors, preserves39FE, sets3A76; descriptor82B34 byte1 bits{bit}..{bit+1}; not proven ON/OFF')

# Cross-model primary-manual evidence; does not establish the Geodan peer implementation.
NATIVE_NAMES[350]=('Återställ källsidans serviceläge (bland annat pump-down)', 'namngiven del',
    '8C733 clears39FE/39FF/3A00/3A01; Mitsubishi JG79N353H02 section9 pp13–14 (PDF pages14–15) specifies350 after pump-down on SUZ-SWM/SHWM; Geodan-specific effect not proven; service-manual-followup.md')
NATIVE_NAMES[351]=('Välj pump-down-serviceläge (dokumenterat för SUZ, ej verifierat på Geodan)', 'namngiven del',
    '8C0B4 writes39FE=1 and clears auxiliary selectors; Mitsubishi JG79N353H02 section9 p13 (PDF page14) specifies351 during refrigerant recovery; physical function on Geodan unknown; service-manual-followup.md')
