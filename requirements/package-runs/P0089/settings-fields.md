# P0089 – inställningsfält och bevarande

**Ingen apply-serializer är kvalificerad.**47 block behålls. Bara65/79 har här explicit kategori6-bindning; övriga block får ingen gissad kategori. Tidigare pumpbytekedjor är återanvänd evidens, inte nya fynd.

|Block (GET/SET)|Kategori|Importgrupp|Kända fält|Återstår|
|---|---|---|---|---|
|50|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|51|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|52|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|53|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|54|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|55|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|56|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|57|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|58|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|59|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|5a|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|5b|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|5c|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|5d|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|5e|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|5f|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|60|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|61|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|62|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|63|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|64|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|65|6|BD296|configured pump level|all remaining meanings/defaults/constraints and affected neighbors|
|66|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|67|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|68|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|69|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|6a|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|6b|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|6c|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|6d|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|6e|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|6f|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|70|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|71|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|72|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|73|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|74|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|75|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|76|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|77|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|78|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|79|6|BD780|configured pump level|all remaining meanings/defaults/constraints and affected neighbors|
|7a|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|7b|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|7c|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|7d|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|
|7e|not individually qualified|unqualified category-dependent import|Ej kvalificerade|all remaining meanings/defaults/constraints and affected neighbors|

## Hela grannområdet som måste hanteras

BD296 ochBD780 skriver till74 respektive27 aktiva destinationer,101 sammanlagt. Det är antal direkta MOV-lagringar i dessa två importörer, inte antal användarinställningar och inte ett bevis att alla indirekta effekter fångats. Varje adress har bredd och instruktionsadress i evidence.json. Alla berörda fält måste kopplas tillbaka till fullständiga SET/GET-layouts före apply.

- bd296: 0729 (2 byte), 072b (2 byte), 072f (2 byte), 0771 (2 byte), 0773 (2 byte), 0775 (2 byte), 0777 (2 byte), 0779 (2 byte), 077b (2 byte), 073d (1 byte), 0723 (2 byte), 0725 (2 byte), 0727 (2 byte), 073c (1 byte), 0721 (2 byte), 073b (1 byte), 07fd (2 byte), 077d (2 byte), 077f (2 byte), 0770 (1 byte), 0720 (1 byte), 073e (1 byte), 073f (2 byte), 0741 (1 byte), 0742 (2 byte), 0744 (2 byte), 0746 (2 byte), 0748 (2 byte), 0753 (1 byte), 0756 (2 byte), 0754 (2 byte), 074a (2 byte), 074c (2 byte), 074e (2 byte), 0752 (1 byte), 0758 (2 byte), 075a (1 byte), 07c3 (2 byte), 0763 (2 byte), 0769 (2 byte), 0800 (2 byte), 0802 (2 byte), 0804 (2 byte), 0806 (2 byte), 0808 (2 byte), 080a (2 byte), 080c (2 byte), 080e (2 byte), 0810 (2 byte), 0812 (2 byte), 0814 (2 byte), 0816 (2 byte), 0787 (2 byte), 078d (2 byte), 0793 (2 byte), 0799 (2 byte), 079f (2 byte), 07a5 (2 byte), 07ab (2 byte), 07b1 (2 byte), 07b7 (2 byte), 07bd (2 byte), 075b (2 byte), 075d (2 byte), 07cc (2 byte), 07d3 (2 byte), 07d5 (1 byte), 07d6 (1 byte), 07d7 (2 byte), 07ca (1 byte), 07cb (1 byte), 07c9 (1 byte), 07d2 (1 byte), 072d (2 byte)
- bd780: 0750 (1 byte), 0751 (1 byte), 07d9 (2 byte), 07db (2 byte), 07dd (1 byte), 07de (1 byte), 07df (1 byte), 07e0 (1 byte), 07e1 (2 byte), 07e3 (2 byte), 07e5 (1 byte), 07e6 (1 byte), 07e7 (1 byte), 07e8 (1 byte), 07e9 (1 byte), 07ea (2 byte), 07ec (2 byte), 07ee (1 byte), 07ef (2 byte), 07f1 (2 byte), 07f3 (2 byte), 07f5 (2 byte), 07f7 (1 byte), 07f8 (1 byte), 07f9 (2 byte), 07fb (1 byte), 07fc (1 byte)

## Konkreta kvalifikationer

SET65 staging1973..197B ochSET79 staging1CAB..1CB6 har blandade format/bytes och framtvingade nollor;GET är inte en SET-mall. P88:s0770/07E6-persistens gäller två fält, inte hela kategorin. BD780 assembler vidBD802..BD80D kombinerar1CAC/1CAD men lagrar endast lågbyte till07E5; behandla inte detta som ett helt16-bitars aktivt värde bara för att mellanberäkningen är ett ord.

BD296/BD780 använder C50BC(base,step,byte) ochC514A(multiplier,byte): råa konverteringar, flera baser(-2000/-4000), steg50 och multiplikator60/1. De utgör inte installerarvalidering eller bevisade användargränser. Profildefault, varje fälts betydelse och egen persistenskedja kvarstår.

För Procon är pumpsteg, ekonomidrift/thermo-diff/kurvpunkter/DHW/energiparametrar fortsatt prioriterad inställningsbacklog. Bara pumpstegen har specifik kvalificerad fältidentitet här. RuntimePWM, flöde och beräknad pumpenergi är andra storheter. Modellen blockerar apply även om anroparen själv påstår att alla grannar är kända.
