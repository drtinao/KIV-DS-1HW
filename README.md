# KIV-DS-1HW
1) Algoritmy použité v programu

Předmětem následujících podkapitol je popis algoritmů, jež byly implementovány v rámci první SP.

1.a) Volba master uzlu, princip fce aplikace

Volba master uzlu je zajištěna implementací tzv. „bully algoritmu“. Za master uzel je tedy považován ten uzel v síti, jež má nejvyšší IP adresu.

Řídící program při spuštění přijímá argument vyjadřující počet očekávaných uzlů v síti. Předpokládá se, že veškeré uzly v síti mají hostname „node-1“, „node-2“ až „node-x“. Při spuštění uzlu se tedy zahájí prohledávání sítě funkcí „retrieve_network_nodes“, jež zkouší překládat hostname na IP adresy. Pokud proběhne překlad hostname → IP v pořádku, funkce start_node_ping ověří, že nalezený uzel je schopný pingovat. Prohledávání sítě probíhá dokud není nalezen očekávaný počet uzlů (parametr programu) či dokud nevyprší timeout.

Po získání seznamu ostatních uzlů v síti je vyhodnocena nejvyšší IP adresa v síti. Pokud má spouštěný uzel danou IP, pak je prohlášen za mastera a očekává připojení od ostatních uzlů v síti – funkce „master_node_listen“. Před samotným umožněním připojení ostatních uzlů je vypočítán počet zelených / červených uzlů funkcí „master_count_colors“.

Pokud spouštěný uzel nemá nejvyšší IP v síti, pak je uzel prohlášen za slave uzel a pokouší se o připojení k masteru – funkce „slave_node_connect“.

1.b) Nastavení barvy uzlů

Master uzel po spuštění a získání dat o stavu strojů v síti vypočítá potřebný počet červených a zelených uzlů – funkce „master_count_colors“. Informace získané výpočtem (= odpovídající barvy) jsou poté zasílány jakožto odpovědi jednotlivým uzlům.

Slave uzly pravidelně zasílají masteru zprávy, ve který sdělují svou aktuální barvu. Master odpovídá barvou, kterou by uzly měly mít nastaveny. Zde je zřejmé, že barva se může v průběhu běhu programu měnit, jelikož některý z uzlů může přestat komunikovat atp. V takovém případě by byl nutný přepočet, aby byly zachovány požadované poměry barev v síti.

Kontakt masteru slave uzlem probíhá pravidelně každých 15s, interval je možno změnit – viz sekce „Konstanty umožňující konfiguraci programu“.

1.c) Kontrola stavu uzlů masterem

Slave uzly pravidelně informují mastera o své barvě – funkce „slave_send_color_mes“. Tímto způsobem masteru sdělují i informaci o tom, že jsou stále aktivní a nedošlo k ukončení funkčnosti uzlu. //To se může hodit v dalších úlohách, kdy bude potřeba řešit výpadky uzlů v síti.

2) Konstanty umožňující konfiguraci programu

2.a) Změna počtu uzlů

Počet uzlů lze změnit přímo ve Vagrantfile, jež se nachází v kořenovém adresáři. Řádka 19. „NODES_COUNT“ – defaultní hodnota je 6 uzlů. Tedy 4 uzly červené, 2 zelené.

2.b) Timeout – nalezení všech uzlů v síti

„DISCOVERY_TIMEOUT_SEC“ v souboru supportTools.py. Vyjadřuje čas v sekundách, do kterého musí uzel nalézt očekávaný počet uzlů v síti (tzn. úspěšně přeložit hostname na IP a pingnout uzel).

2.c) Timeout – připojení slave -> master

„MASTER_CONNECT_SEC“ v souboru nodeTools.py. Počet sekund, do kterých musí slave navázat spojení s masterem.

2.d) Interval odeslání aktuální barvy slave -> master

„MASTER_CONTACT_SEC“ v souboru nodeTools.py. Interval v sekundách, jež vyjadřuje frekvenci kontaktování mastera slave uzlem.

3) Spuštění aplikace

Pro spuštění je potřeba mít nainstalován Vagrant a Docker. Poté stačí v kořenovém adresáři pouze zadat příkaz „vagrant up“ a aplikace bude sestavena / spuštěna. Program následně běží do té doby než je ukončen (např. ctrl + c). Do terminálu jsou každých 15s (pokud není změna, viz konstanty) vypisovány informace od každého z uzlů.
