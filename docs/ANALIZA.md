# Analiza firmware ZiShan Z3 (v0.5) — możliwość dodania języka polskiego

Data analizy: 2026-07-10
Plik źródłowy: `ZiShan_Z3_0.5.rar` → `z3app.bin` (761 339 B). To repozytorium dotyczy wyłącznie Z3 — firmware Z2 posłużyło tylko jednorazowo jako punkt porównawczy (nie jest częścią tego repo).

Cel: sprawdzić, czy i jak można zmodyfikować tekst menu odtwarzacza ZiShan Z3
(np. dodać/podmienić język na polski).

---

## 1. Skrócone podsumowanie

| Pytanie | Odpowiedź | Pewność |
|---|---|---|
| Jaki mikrokontroler? | STM32F427 (ARM Cortex-M4, potwierdzone przez rozpoznane wzorce kodu Thumb-2 i adresy we flashu 0x08000000-0x08200000) | wysoka |
| Jaki DAC? | Wariant sprzętowy — w tekstach firmware są **obie** nazwy: `CS43198` i `ES9038` (czyli ten sam plik obsługuje różne wersje płyty Z3) | wysoka |
| Czy plik jest szyfrowany/skompresowany? | Nie widać dowodów szyfrowania. Duża część pliku to prawdopodobnie bitmapy fontów/ikon (stąd wysoka entropia), a nie szyfrogram | średnia-wysoka |
| Czy jest walidacja integralności (checksum)? | **TAK — potwierdzone testem.** Bootloader zawiesza się na "Checking bin" dla pliku ze zmienioną nawet 1 wartością bajtów. Algorytm nieznany (wykluczono CRC32/CRC16/Fletcher16/Adler32/proste sumy) | wysoka (fakt) / nieznany (algorytm) |
| Czy jest gdzie szukać tekstu menu? | Tak — mały (~2 KB) obszar na końcu pliku (~0xB90F7–0xB9834) zawiera realne stringi UI: błędy, nazwy formatów, "Language", "About" itd., w chińskim uproszczonym, chińskim tradycyjnym i angielskim | wysoka |
| Czy silnik fontów obsługuje polskie znaki (ą ć ę ł ń ó ś ź ż)? | Punkty kodowe SĄ w tabeli czcionki (sekcja 5), ale **test na żywym urządzeniu (2026-07-10) pokazał, że w praktyce NIE działają** — nazwa pliku z „ą" wyświetla „?" i plik się nie odtwarza, mimo że chiński (też spoza ASCII) działa normalnie. Prawdopodobnie brakuje konwersji Unicode→wewnętrzne kodowanie dla tego zakresu, nie tylko bitmap | **potwierdzone testem: obecnie nie działa** |
| Czy da się mieć polskie menu bez ogonków (a,c,e,l,n,o,s,z,z)? | Tak, dużo bardziej realistyczne — czyste ASCII już teraz działa bezbłędnie na urządzeniu | wysoka |
| Czy da się bezpiecznie edytować tekst? | Tak, prawdopodobnie — ale trzeba zachować długość bajtową oryginalnego stringu (patrz sekcja 6) | średnia |
| Czy da się dodać *nowy* (4.) język w menu wyboru? | Prawdopodobnie wymaga zmiany kodu (nie tylko danych) — struktura wpisów menu zawiera wskaźniki, nie tylko tekst | niska (bez disasemblera) |

**Najważniejsze odkrycie:** tabela znaków obsługiwanych przez silnik czcionek (offset `0xB7C46`–`0xB8002` w `z3app.bin`) zawiera pełny zestaw Unicode Latin Extended-A (w tym WSZYSTKIE polskie litery), grekę i **cały cyrylicki alfabet**. To silna wskazówka, że Zishan użył gotowego, uniwersalnego komponentu (biblioteki) do renderowania tekstu, który już "z fabryki" umie więcej języków niż faktycznie wykorzystane w menu (obecnie tylko chiński + angielski). Ta sama tabela istnieje też w firmware Z2 (który nie ma wyświetlacza!) — czyli to wspólny, współdzielony komponent w całej linii produktów Zishan, a nie coś napisanego specjalnie do Z3.

---

## 2. Sprzęt i mechanizm aktualizacji

- MCU: **STM32F427** (potwierdzone przez użytkownika + zgodne z odnalezionymi adresami 0x0812xxxx / 0x080Exxxx w pliku, które leżą w zakresie wewnętrznego flasha STM32: 0x08000000–0x08200000).
- DAC: **CS43198** i **ES9038** — obie nazwy chipów widoczne jako literały tekstowe w pliku (offset ok. `0xB9758` i `0xB9760`), więc jeden plik firmware obsługuje różne wersje sprzętowe.
- Wersja: string `"Z3 v0.5"` pod `0xB9774` potwierdza zgodność z nazwą pliku.
- Deskryptory USB (urządzenie działa też jako karta dźwiękowa USB): znaleziono fragmenty `"ZiShan Z3 HiFi"`, `"...logy Co.,Ltd."` (obcięte "...Technology Co.,Ltd."), `"AUDIO_"`, `"Interf(ace)"` — typowe stringi USB Audio Class w pobliżu offsetu `0xB8126`.

**Sposób aktualizacji** (z pliku `升级步骤.txt` dołączonego do firmware Z2, ten sam mechanizm dotyczy Z3):
1. Skopiować `z3app.bin` do głównego katalogu karty SD (TF).
2. Włożyć kartę do odtwarzacza i włączyć zasilanie.
3. Dioda status świeci chwilę, potem miga nieregularnie ~5 s — to trwa flashowanie.
4. Usunąć plik `z3app.bin` z karty SD.

Wniosek: urządzenie ma **własny bootloader**, który sam odczytuje plik z karty SD i zapisuje go do pamięci programu. Plik `z3app.bin` to najpewniej surowy obraz aplikacji (nie widać żadnego przemysłowego narzędzia PC do "pakowania" firmware) — co jest dobrą wiadomością dla edycji.

---

## 3. Mapa pliku `z3app.bin` (761 339 B)

Na podstawie entropii, gęstości typowych instrukcji ARM Thumb-2 (`bx lr` = `70 47`, `push {r4,lr}` = `10 b5`) i udziału bajtów "printable":

| Zakres offsetów | Rozmiar | Zawartość (interpretacja) | Pewność |
|---|---|---|---|
| `0x000000–0x05A000` | ~370 KB | Mieszanka kodu i danych (główna logika aplikacji) | średnia |
| `0x05B000–0x064000` | ~36 KB | Gęsty kod ARM Thumb-2 (bardzo dużo `push`/`pop`) — jądro logiki | wysoka |
| `0x065000–0x07A000` | ~90 KB | Kod + dane (rodata, tablice) | średnia |
| `0x07B000–0x082000` | ~28 KB | Niska entropia, mało tekstu — prawdopodobnie bitmapy ikon | niska-średnia |
| `0x083000–0x0B6000` | ~206 KB | Wysoka entropia (7.0–7.9 bit/B) — najpewniej duża bitmapa fontu chińskiego (GBK) i/lub inne zasoby graficzne | średnia |
| `0x0B6000–0x0B7C45` | ~7.2 KB | **Lista nazw gatunków ID3v1/extended** (standardowe 148 gatunków MP3: "Alternative", "Ska", "Gothic"... to dane do wyświetlania tagów, NIE tekst menu) | wysoka |
| `0x0B7C46–0x0B8002` | 956 B | **Tabela punktów kodowych Unicode silnika czcionek** (patrz sekcja 5) | wysoka |
| `0x0B8004–0x0B80CC` | ~200 B | Mała tabela (wskaźniki?), nie do końca zanalizowana | niska |
| `0x0B80D0–0x0B9DFB` (koniec pliku) | ~7.5 KB | Krótkie funkcje kodu + **stringi UI używane przez program**: błędy, nazwy formatów, etykiety menu, deskryptory USB (patrz sekcja 4) | wysoka |

Uwaga: offset 0 pliku **nie** wygląda jak standardowa tablica wektorów przerwań Cortex-M (sprawdzone systematycznie, różne przesunięcia bajtowe, różne kandydackie adresy bazowe — brak trafienia). To sugeruje, że `z3app.bin` nie jest ładowany 1:1 od adresu 0x08000000, albo że bootloader relokuje/przesuwa obraz, albo (najbardziej prawdopodobne) że sekcja `.isr_vector` nie jest pierwszą sekcją w tym konkretnym obrazie linkowania. **To nie blokuje edycji tekstu**, ale blokuje pewne rzeczy wymagające pełnej dezasemblacji (patrz sekcja 7).

---

## 4. Znalezione stringi UI (tekst menu, błędy, etykiety)

Wszystkie w zakresie `0xB90F7`–`0xB9834` pliku `z3app.bin` (chiński w kodowaniu GBK, chyba że zaznaczono inaczej):

| Offset | Tekst | Tłumaczenie / znaczenie |
|---|---|---|
| `0xB7959` | 播放界面 | "Ekran odtwarzania" |
| `0xB7998` | 设置 | "Ustawienia" |
| `0xB79CC` | 系统 | "System" |
| `0xB90F7` | 删除 | "Usuń" |
| `0xB910E` | 找不到第一帧,无法播放 | "Nie znaleziono pierwszej ramki, nie można odtworzyć" (błąd) |
| `0xB9388` | 版本 | "Wersja" |
| `0xB93A4` | 遇到了未知错误 | "Wystąpił nieznany błąd" |
| `0xB9482` | damaged | (ang., fragment komunikatu o uszkodzonym pliku) |
| `0xB9500` | 未知艺术家 | "Nieznany artysta" |
| `0xB950E` | 专辑 | "Album" |
| `0xB95B4` | 上+下键关闭 | "Przyciski Góra+Dół aby zamknąć/wyłączyć" |
| `0xB95C3` | 鍵關閉 | to samo, ale w chińskim **tradycyjnym** (关闭→關閉) |
| `0xB966E` | 背光时间 | "Czas podświetlenia" |
| `0xB967C` | 语言 | "Język" |
| `0xB9750` | STOP | (ang.) |
| `0xB9758` | CS43198 | nazwa DAC |
| `0xB9760` | ES9038 | nazwa DAC |
| `0xB9774` | Z3 v0.5 | wersja firmware |
| `0xB97D6` | 关于 | "O programie" (chiński uproszczony) |
| `0xB97DD` | 關於 | to samo po chińsku **tradycyjnym** |
| `0xB97EA` | English | nazwa opcji językowej (native name, nie tłumaczona) |
| `0xB97F4` | 全部 | "Wszystko" (np. powtarzanie wszystkiego) |
| `0xB97FA` | 循环 | "Powtarzanie" |
| `0xB9801` | 随机 | "Losowo" |
| `0xB9808` | 单曲 | "Pojedynczy utwór" |
| `0xB9834` | Order | (ang., np. "Play Order") |
| `0xB984B` | One | (ang., np. "Repeat One") |
| `0xB98AA` | EQ | Equalizer |
| `0xB92DE` | MP3 | format |
| `0xB92EB` | WAV/L... | format (obcięty, pewnie WAV/LPCM) |
| `0xB92F2` | DTS | format |
| `0xB930D` | factory | prawdopodobnie "factory reset" |
| `0xB8E79` | multi-channel DSF | opis formatu DSD |
| `0xB8EBA` | ISO | format (DSD ISO) |

**Bardzo ważna obserwacja:** obok siebie występują wersje **chińska uproszczona** (关于, 关闭) i **chińska tradycyjna** (關於, 關閉) tych samych słów. To silny dowód, że firmware ma (co najmniej) **trzy** zestawy tekstu: chiński uproszczony, chiński tradycyjny, angielski — mimo że w menu użytkownika widoczne są zwykle tylko 2 opcje językowe. Tradycyjny chiński może być trzecią, rzadziej używaną opcją (rynek Tajwan/HK) albo pozostałością z współdzielonego kodu.

To dobra wiadomość: **jest potencjalnie "wolny" zestaw tekstu (chiński tradycyjny), którego polski użytkownik nie potrzebuje** — to najlepszy kandydat do podmiany na polski, jeśli okaże się, że jest w ogóle wybieralny z menu (wymaga potwierdzenia — patrz sekcja 7).

Surowa lista trafień: [`tools/wyniki/z3_menu_strings_znalezione.txt`](../tools/wyniki/z3_menu_strings_znalezione.txt)

---

## 5. Tabela znaków Unicode silnika czcionek — klucz do polskiego języka

Pod offsetem `0xB7C46`–`0xB8002` (956 bajtów) znajduje się tabela **478 punktów kodowych Unicode** zapisanych jako UTF-16LE (2 bajty/wpis, bez tekstu — same numery znaków). To wygląda na "słownik" znaków, które silnik czcionek jest w stanie zamienić w indeks do bitmapy glifu.

Zawartość tabeli (w kolejności występowania):
- Podstawowe ASCII: `a`-`z`, symbole
- Latin-1 Supplement: `à-ÿ` (znaki zachodnioeuropejskie: niemieckie, francuskie, itd.)
- **Latin Extended-A: kompletny blok `U+0100`–`U+017E`** — to zawiera WSZYSTKIE polskie znaki diakrytyczne
- Grecki: `Α-Ϊ`, `α-ϊ`
- **Cyrylica: kompletny alfabet rosyjski + litery ukraińskie/serbskie** (`U+0410`–`U+045F`)
- Cyfry rzymskie (małe i wielkie, `U+2160`–`U+217F`)
- Fullwidth Latin (`U+FF21`–`U+FF5A`, używane w typografii CJK)
- Dodatkowe symbole walut, więcej Latin-1 wielkich liter

### Weryfikacja polskich znaków (18/18 obecne)

| Znak | Punkt kodowy | Status |
|---|---|---|
| ą / Ą | U+0105 / U+0104 | ✅ obecne (indeksy 65 / 305) |
| ć / Ć | U+0107 / U+0106 | ✅ obecne (indeksy 66 / 306) |
| ę / Ę | U+0119 / U+0118 | ✅ obecne (indeksy 75 / 315) |
| ł / Ł | U+0142 / U+0141 | ✅ obecne (indeksy 95 / 335) |
| ń / Ń | U+0144 / U+0143 | ✅ obecne (indeksy 96 / 336) |
| ó / Ó | U+00F3 / U+00D3 | ✅ obecne (indeksy 51 / 291) |
| ś / Ś | U+015B / U+015A | ✅ obecne (indeksy 107 / 347) |
| ź / Ź | U+017A / U+0179 | ✅ obecne (indeksy 122 / 362) |
| ż / Ż | U+017C / U+017B | ✅ obecne (indeksy 123 / 363) |

Zweryfikowane skryptem [`tools/dump_charset_table.py`](../tools/dump_charset_table.py).

### Co to znaczy w praktyce?

Sam fakt, że punkt kodowy jest **wymieniony w tej tabeli indeksu**, nie dowodzi, że gdzieś w pliku istnieje **rzeczywista bitmapa** tego glifu (obrazek litery "ą" do wyświetlenia na ekranie). Tabela może być częścią ogólnego, współdzielonego komponentu (patrz sekcja 1), a konkretna czcionka wgrana do Z3 mogła zawierać bitmapy tylko dla znaków faktycznie użytych (chiński + podstawowy ASCII), żeby zaoszczędzić miejsce we flashu.

**Nie ustalono jeszcze jednoznacznie, czy bitmapy polskich liter istnieją.** To najważniejsze pozostałe pytanie — patrz sekcja 6, test #1 (do wykonania na żywym urządzeniu, bez modyfikacji firmware!).

---

## 6. Zalecane następne kroki (w kolejności priorytetu)

### Krok 1 — Test bez ryzyka, na żywym urządzeniu (ZRÓB TO NAJPIERW)

Nie wymaga modyfikacji firmware. Sprawdza, czy glify polskich liter istnieją:

1. Na karcie SD zmień nazwę jakiegoś pliku muzycznego lub folderu tak, aby zawierała polskie znaki, np. `Zażółć gęślą jaźń.mp3`.
2. Włóż kartę do Z3 i przejdź do przeglądarki plików / wyświetl tę nazwę na ekranie.
3. Obserwuj:
   - **Jeśli litery ą/ż/ł itd. wyświetlą się poprawnie** → glify istnieją, silnik już umie renderować polski tekst. To bardzo dobra wiadomość — drastycznie ułatwia dalszą pracę (można skupić się tylko na podmianie tekstu, bez tworzenia nowych bitmap fontu).
   - **Jeśli pokażą się kwadraty/puste miejsca/inne znaki** → glify nie są wgrane, trzeba by je dorobić (znacznie większe przedsięwzięcie: edycja bitmapy fontu).
4. To samo warto sprawdzić z tagami ID3 (artysta/tytuł z polskimi znakami) — silnik może inaczej renderować nazwy plików niż metadane.

#### Wynik testu (2026-07-10)

Użytkownik przetestował plik `Zażółć gęślą jaźń.flac` na realnym Z3. Efekt:
- Nazwa wyświetliła się jako same znaki **„?"**.
- Plik **nie odtworzył się** (nie tylko problem z wyświetlaniem — coś zawiodło głębiej).

Interpretacja: „?" to typowy znak zastępczy silnika tekstu dla nierozpoznanego/niewyrenderowalnego kodu, więc **na razie wygląda na to, że bitmapy polskich liter nie są wgrane** (albo nie są używane w tej ścieżce kodu). Ale fakt, że plik się nie odtworzył, to dodatkowy, odrębny sygnał ostrzegawczy — może to być:
(a) skutek problemu z fontem/wyświetlaniem, który przy okazji psuje też odtwarzanie, **albo**
(b) całkiem inny, głębszy problem: sposób, w jaki firmware odczytuje długie nazwy plików (LFN) z FAT, może nie obsługiwać poprawnie znaków spoza ASCII/GBK, co gubi/uszkadza wewnętrzną ścieżkę do pliku jeszcze przed dotarciem do renderera.

**Zalecane kolejne testy (żeby rozdzielić przyczyny), w tej kolejności:**
1. **Jeden znak naraz** — plik nazwany np. `test_a.flac` (bez diakrytyków, kontrolny) odtwarza się normalnie? Potem `test_ą.flac` (tylko jedno „ą", reszta ASCII) — wyświetla „?" i/albo nie odtwarza?
2. **Test z chińskim** — nazwij plik chińskimi znakami (np. `播放.flac`) — chiński jest oficjalnie wspierany, więc powinien wyświetlić się i odtworzyć poprawnie. Jeśli TAK → problem jest specyficzny dla zakresu Latin Extended-A (polskie znaki), nie ogólny problem z Unicode/LFN. Jeśli NIE (też nie działa) → to wskazuje na ogólny problem z obsługą długich nazw plików, niezależny od konkretnych znaków.
3. **Test przez tag ID3, nie nazwę pliku** — zostaw nazwę pliku w ASCII (np. `test1.flac`), ale wpisz „Zażółć gęślą jaźń" jako tytuł/artystę w tagu ID3 i sprawdź ekran „teraz odtwarzane". To sprawdza inną ścieżkę kodu (parser ID3 + renderer), niezależną od parsowania nazw plików w FAT.

To pozwoli ustalić, czy warto inwestować czas w tworzenie nowych bitmap fontu (jeśli problem = brak glifów), czy raczej w naprawę/obejście parsowania nazw plików (jeśli problem = FAT/LFN), czy oba.

#### Wynik testów 1 i 2 (2026-07-10) — JEDNOZNACZNY

| Plik testowy | Wynik |
|---|---|
| `test_a.flac` (czyste ASCII) | działa normalnie |
| `播放.flac` (chiński) | działa normalnie |
| `test_ą.flac` (jeden polski znak, resztą ASCII) | „?" i **nie odtwarza się** |

**Wniosek: problem jest ściśle ograniczony do zakresu polskich znaków (Latin Extended-A), a nie ogólnym problemem obsługi Unicode/LFN.** Skoro chiński (spoza ASCII) działa bez problemu, cały mechanizm odczytu długich nazw plików z FAT i konwersji na wewnętrzne kodowanie działa poprawnie — po prostu nie ma ścieżki (konwersji i/albo glifu) dla tego konkretnego zakresu znaków.

To **zmienia ocenę z sekcji 1** — obecność polskich punktów kodowych w tabeli czcionek (sekcja 5) **nie przełożyła się na realne wsparcie w praktyce**. Najbardziej prawdopodobne wyjaśnienie: firmware ma wewnętrzną konwersję Unicode → GBK/ASCII (typowa dla chińskich urządzeń — Unicode z FAT LFN jest tłumaczony na wewnętrzne kodowanie GBK, w którym dalej operuje reszta systemu, łącznie z rendererem). Ta konwersja obsługuje ASCII i chiński (bo GBK to natywne kodowanie), ale nie ma mapowania dla Łacińskiego Extended-A → stąd „?" (typowy znak zastępczy przy nieudanej konwersji) i prawdopodobnie uszkodzona nazwa pliku wewnętrznie (stąd brak odtwarzania — program szuka pliku pod złą/skróconą nazwą).

Tabela punktów kodowych z sekcji 5 najpewniej służy innej części współdzielonej biblioteki (np. samemu rendererowi/indeksowi glifów gdyby dostał poprawny kod), a nie jest używana przez ten konkretny etap konwersji z FAT. Innymi słowy: **mamy dwie odrębne bariery do pokonania, nie jedną**:
1. Warstwa konwersji Unicode→wewnętrzne kodowanie musi zacząć przepuszczać/mapować polskie znaki (żeby dane w ogóle dotrwały do renderera w rozpoznawalnej formie).
2. Renderer musi mieć (lub dostać) realne bitmapy glifów dla tych znaków.

To realnie podnosi próg trudności zadania — to już nie jest "podmień tekst w tabeli", a **modyfikacja logiki firmware** (wymaga dezasemblacji i patchowania kodu konwersji, plus prawdopodobnie dorobienia bitmap). Zobacz Krok 2 i 2b poniżej.

#### Praktyczna alternatywa: polski BEZ ogonków

Skoro czyste ASCII działa bez zarzutu (`test_a.flac`), **tłumaczenie menu na polski bez znaków diakrytycznych** (np. "Jezyk", "Ustawienia", "Wersja", "Blad") jest już teraz dużo bardziej realistycznym, mniejszym projektem — wymaga tylko bezpiecznej podmiany tekstu w tabeli stringów (sekcja 4), bez dotykania konwersji Unicode czy bitmap fontu. To rozwiązuje 90% problemu (menu po polsku) bez konieczności głębokiej ingerencji w kod.

### Krok 2 — Dezasemblacja z użyciem Ghidra (zalecane dla dalszej pracy)

Ręczna analiza hex (którą wykonałem) ma granice — pozwoliła znaleźć i zrozumieć **dane** (stringi, tabelę znaków), ale nie **kod**, który z nich korzysta. Bez tego nie wiadomo z pewnością:
- czy string jest adresowany przez wskaźnik (bezpieczna edycja w miejscu = OK, zmiana długości = ryzykowna),
- czy dodanie 4. języka w menu wymaga zmiany kodu (najpewniej: tak — patrz obserwacja w sekcji 4 o strukturach z wskaźnikami `0x0812xxxx`/`0x080Exxxx` sąsiadującymi z tekstem),
- gdzie faktycznie jest bitmapa fontu i jaki ma format (ile bitów na pixel, jaka szerokość/wysokość glifu).

Zalecenie: zainstalować [Ghidra](https://ghidra-sre.org/) (darmowy, od NSA), załadować `z3app.bin` jako "raw binary" z architekturą ARM Cortex-M4 (little endian), i użyć jego auto-analizy oraz wyszukiwania odwołań (cross-references) do znalezionych już offsetów stringów (np. `0xB967C` dla "语言"/Language) — to powinno naprowadzić na funkcję renderującą menu.

Mogę pomóc to skonfigurować i przeprowadzić w kolejnej sesji, jeśli zdecydujesz się na ten krok.

### Krok 3 — Bezpieczna edycja testowa (po kroku 1 i 2)

Zasada bezpieczeństwa przy edycji jakiegokolwiek stringu (niezależnie od tego, czy mechanizm to wskaźniki czy indeksy):

> **Nowy tekst nie może być dłuższy w bajtach niż oryginalny.** Krótszy tekst dopełnij bajtami `0x00` do oryginalnej długości. Nigdy nie przesuwaj żadnych danych za edytowanym stringiem.

To gwarantuje, że nic "po drodze" (kolejne stringi, wskaźniki, cokolwiek) się nie rozjedzie — bez względu na to, jaki jest dokładny mechanizm adresowania.

Problem praktyczny: chińskie znaki są bardzo "gęste" (1 znak = całe słowo), więc chińskie 版本 (4 bajty) → polskie "Wersja" (6 bajtów) może **przekroczyć** budżet. Trzeba sprawdzać dostępne miejsce (odległość do następnego pola w strukturze) dla każdego stringu indywidualnie, i w razie potrzeby skracać (np. "Wers." albo używać angielskich odpowiedników już obecnych w pliku, gdzie to możliwe).

Najlepszy pierwszy cel testowy: string **"English"** (`0xB97EA`, 7 bajtów, sam ASCII, izolowany) — podmiana na np. `"Polski"` (6 bajtów, mieści się) jest niskiego ryzyka i łatwo zweryfikować efekt na ekranie (menu wyboru języka).

#### Wykonane (2026-07-10): pierwszy patch testowy

Przygotowany plik: `extracted_z3/z3app_test_polski.bin` (generowany przez `tools/patch_strings.py`, nie jest w repo — patrz `.gitignore` — ale wygenerujesz go w 1 sekundę: `python tools/patch_strings.py extracted_z3/z3app.bin extracted_z3/z3app_test_polski.bin`).

Zmiana: bajty `0xB97EA`–`0xB97F0` (dokładnie 7 bajtów) `"English"` → `"Polski\0"`. Zweryfikowano bit-po-bicie: **zmieniło się wyłącznie tych 7 bajtów**, rozmiar pliku identyczny (761 339 B), sąsiedni bajt (`0x4c`, prawdopodobnie pole binarne, nie tekst) nietknięty.

**Uwaga — nie mam 100% pewności na jakim konkretnie ekranie to "English" się wyświetla.** Znaleziono je w klastrze z 关于/關於 (About) i 循环/随机/单曲 (tryby powtarzania), niedaleko, ale nie w tym samym oczywistym miejscu co 语言 (Language) pod `0xB967C` — więc może to być nazwa języka w menu wyboru, może coś na ekranie "About", może coś nieużywane. **To właśnie sprawdzi test na urządzeniu.**

**Jak przetestować:**
1. Skopiuj `z3app_test_polski.bin` na kartę SD, **zmień nazwę na `z3app.bin`** (tak jak wymaga bootloader).
2. Miej gdzieś bezpiecznie oryginalny `z3app.bin` (kopię zapasową) — na wszelki wypadek.
3. Flashuj jak zwykle (włóż kartę, włącz zasilanie, czekaj aż dioda przestanie migać, usuń plik z karty).
4. Sprawdź: czy urządzenie normalnie się uruchamia? Czy coś w menu (Language, About, tryby powtarzania) teraz pokazuje "Polski" zamiast "English"? Czy cokolwiek innego wygląda uszkodzone?

Wynik tego testu powie nam dwie rzeczy naraz: (a) czy metoda bezpiecznej podmiany bajtowej w ogóle działa na tym firmware (czy urządzenie nie waliduje sumy kontrolnej itp.), i (b) gdzie faktycznie ten string się wyświetla.

#### Rozszerzenie (2026-07-10): druga partia podmian — sloty 4-bajtowe (grupa "eksperymentalna")

Zmierzono precyzyjnie dostępny budżet bajtowy dla kilku kolejnych kluczowych etykiet menu — wszystkie okazały się **ścisłymi, gęsto upakowanymi slotami 4-bajtowymi (2 znaki GBK, bez separatora ani zapasu)**:

| Offset | Oryginał (GBK) | Bajt po slocie | Budżet | Nowy tekst |
|---|---|---|---|---|
| `0xB7998` | 设置 (Ustawienia) | `0xb4` (dane) | 4 B, bez zapasu | `Ust` |
| `0xB79CC` | 系统 (System) | `0x2c` (dane) | 4 B, bez zapasu | `Syst` |
| `0xB967C` | 语言 (Język) | `0x6c` (dane) | 4 B, bez zapasu | `Jez` |
| `0xB9388` | 版本 (Wersja) | `0x00` (null!) | 4 B + 1 null | `Wers` |
| `0xB97D6` | 关于 (About, uproszczony) | `0x7c` ('\|' delimiter) | 4 B, bez zapasu | `Info` |

**To potwierdza wcześniejszą obawę z tego dokumentu: budżet 4 bajtów (2 chińskie znaki) wystarcza na maksymalnie 4 litery ASCII — nie da się zmieścić pełnych polskich słów** ("Ustawienia", "System", "Język", "Wersja", "Info" → tylko "Info" pasuje bez skracania). Powyższe to więc **skróty**, nie ostateczne tłumaczenia — traktuj jako drugi test poligonowy, nie finalny efekt.

**Wyższe ryzyko niż grupa "bezpieczna":** nie potwierdzone czy renderer/logika menu wymaga, żeby te sloty zawierały prawidłowe znaki GBK (2-bajtowe), czy przyjmie też czyste bajty ASCII bez problemu. To jest właśnie do sprawdzenia na urządzeniu.

Wygenerowanie pliku testowego z obiema grupami naraz:
```
python tools/patch_strings.py extracted_z3/z3app.bin extracted_z3/z3app_test_polski_eksperymentalny.bin bezpieczna eksperymentalna
```
Zweryfikowano bit-po-bicie: zmienia się dokładnie 27 bajtów w 6 rozłącznych zakresach (5×4 B + 1×7 B), zero wycieku poza granice slotów, rozmiar pliku identyczny.

#### 🛑 WAŻNY WYNIK TESTU NA URZĄDZENIU (2026-07-10): jest walidacja sumy kontrolnej

Test na realnym Z3:
- **Oryginalny `z3app.bin`** (nietknięty): `Checking bin OK!` → `Erase flash 100%` → `Program flash 100%` → reboot. Działa bezbłędnie.
- **Zmodyfikowany `z3app_test_polski.bin`** (tylko 7 bajtów zmienionych, `English`→`Polski`): zatrzymuje się na etapie `Checking bin 1169242` i **nie postępuje dalej** (sprawdzone: nic się nie zmienia po >1 minucie).

**Wniosek: bootloader liczy jakąś sumę kontrolną / walidację całej zawartości pliku przed flashowaniem, i odrzuca (a właściwie: zawiesza się na) plik z nieprawidłową sumą.** To był otwarty punkt niepewności z sekcji 2 tego dokumentu ("Nie wykryto szyfrowania/kompresji") — teraz wiemy, że *walidacja integralności* na pewno istnieje, nawet jeśli sama treść nie jest szyfrowana.

Liczba `1169242` (`0x11D75A`) wyświetlana na ekranie to najpewniej albo obliczona (nieprawidłowa) suma kontrolna zmodyfikowanego pliku, albo licznik pętli sprawdzającej, która nigdy nie trafia na oczekiwaną wartość i nie ma logiki timeout/retry (stąd zawieszenie, nie czytelny komunikat błędu).

**Sprawdzone i WYKLUCZONE jako algorytm dający `1169242` dla `z3app_test_polski.bin`:**
- CRC32 (zlib) w wielu wariantach zakresu (pomijanie 0-64 B na początku/końcu)
- Prosta suma addytywna 32-bit i 16-bit (dla różnych offsetów startowych)
- XOR 32-bit po słowach
- CRC16 (CCITT poly 0x1021, IBM poly 0x8005; init 0x0000 i 0xFFFF)
- Fletcher-16
- Adler-32 (pełny i zamaskowany do 16 bit)

**To oznacza, że dalsza edycja tekstu WYMAGA znalezienia i przeliczenia tej sumy kontrolnej** — bez tego żadna modyfikacja treści (nawet 1 bajt) nie przejdzie przez `Checking bin`. To podnosi próg trudności całego projektu: bez dezasemblacji (Ghidra) trafienie na właściwy algorytm i lokalizację pola sumy kontrolnej metodą prób i błędów jest bardzo mało prawdopodobne w rozsądnym czasie.

**Zalecany następny krok (kolejna sesja):** Ghidra, konkretnie w tym celu:
1. Znaleźć w kodzie funkcję odpowiedzialną za komunikat "Checking bin" (string bezpośrednio w kodzie bootloadera — ale UWAGA: bootloader może być w OSOBNYM regionie flash, niedostępnym w `z3app.bin`! Jeśli tak, trzeba by zdobyć dump całej flashy urządzenia, nie tylko pliku aktualizacji — do zweryfikowania).
2. Zidentyfikować algorytm sumy kontrolnej i offset w pliku, gdzie oczekiwana wartość jest przechowywana (prawdopodobnie w nagłówku, pierwsze 16-32 bajty pliku, które od początku analizy nie pasowały do standardowej tablicy wektorów ARM — patrz sekcja 3, mogą to być właśnie pola magic/rozmiar/checksum, nie wektory przerwań).
3. Dodać do `tools/patch_strings.py` automatyczne przeliczenie i zapis poprawnej sumy po każdej edycji.

#### 🛑 Potwierdzone (2026-07-10): kodu sprawdzajacego NIE MA w z3app.bin

Sprawdzono: żaden z komunikatów bootloadera ("Checking", "Erase", "Program flash", "Bin OK") **nie istnieje jako string w `z3app.bin`**. Sprawdzono też, czy `1169242` (`0x11D75A`) jest zapisane jako stała wartość referencyjna gdziekolwiek w oryginalnym pliku (LE32/BE32/LE24) — też nie.

**Wniosek: bootloader, który wyświetla te komunikaty i liczy sumę kontrolną, to zupełnie OSOBNY program, żyjący w innym, chronionym regionie wewnętrznej flashy STM32F427 — nie jest częścią pliku aktualizacji `z3app.bin` w ogóle.** Ghidra uruchomiona na `z3app.bin` **nie znajdzie** tej funkcji, bo jej tam nie ma — to nie jest kwestia szukania lepiej, tylko fizycznej nieobecności kodu w tym pliku.

**Żeby faktycznie znaleźć algorytm sumy kontrolnej, potrzebny byłby zrzut (dump) całej zawartości flash mikrokontrolera prosto z płytki** — czyli:
1. Sprzętowy debugger SWD (np. ST-Link V2, klon za ~20-40 zł) podłączony do punktów testowych SWDIO/SWCLK/GND/3.3V na płycie Z3 (masz gołą płytkę, więc to realne, o ile te punkty są dostępne/opisane).
2. Narzędzie typu STM32CubeProgrammer albo OpenOCD do odczytu całej flashy (nie tylko regionu aplikacji).
3. **Warunek, który może to zablokować:** jeśli producent włączył ochronę odczytu (RDP - Readout Protection) na tym STM32, odczyt przez SWD będzie zablokowany. To bardzo częste w produktach komercyjnych właśnie żeby uniemożliwić to, co robimy. Nie da się tego sprawdzić bez faktycznego podłączenia debuggera.

To realnie oznacza, że **dalsza edycja tekstu menu jest zablokowana** do czasu zdobycia (a) dumpu całej flashy przez SWD, albo (b) innego sposobu na wyłączenie/obejście walidacji sumy kontrolnej. To wykracza poza czystą analizę pliku — wymaga sprzętu i fizycznego dostępu do płytki.

**Co WCIĄŻ ma sens robić w Ghidrze na `z3app.bin`** (mimo że nie rozwiąże to checksumy): zrozumienie WŁASNEGO kodu aplikacji — jak dokładnie referowana jest tabela stringów menu (sekcja "Otwarte pytania"), co robią te dwa wskaźniki `0x0812xxxx`/`0x080Exxxx` sąsiadujące z tekstem. To przygotowuje grunt na później, gdyby udało się zdobyć dump bootloadera.

#### Sesja w Ghidrze (2026-07-10) — wyniki

Zaimportowano `z3app.bin` jako Raw Binary, język `ARM:LE:32:Cortex`, adres bazowy domyślny (0x0 — nieznany prawdziwy adres ładowania, patrz sekcja 3).

- **Domyślna auto-analiza:** rozpoznała bardzo mało kodu (plik w większości potraktowany jako dane) — bez rozpoznanej tablicy wektorów przerwań na starcie, Ghidra nie miała punktu zaczepienia do zaczęcia dysasemblacji.
- **Ręczne wymuszenie dekodowania** pod `0x5c000` (Thumb) dało sensowny wynik: `str r7,[r0,r2]` / `ldmia r7,{r0,r1,r2,r7}` / `pop {r5,r6,r7,pc}` — **to potwierdza, że w pliku jest prawdziwy, poprawny kod Thumb**, tylko Ghidra nie wie gdzie go szukać bez znanego adresu bazowego.
- **Analizator "ARM Aggressive Instruction Finder"** (szuka wzorców kodu w całym pliku bez potrzeby znanej tablicy wektorów): uruchomiony, ale znalazł tylko **~10-20 funkcji** w pliku 760 KB — bardzo mało w stosunku do realnej wielkości aplikacji (setki/tysiące funkcji dla pełnego UI+audio DAP). Rozgałęzienia/wywołania prawdopodobnie się "gubią" bez poprawnego adresu bazowego.
- **XREF dla `0xB97EA` ("English"):** sprawdzone przed i po agresywnej analizie — **brak jakiegokolwiek odwołania z kodu, w obu przypadkach.** Zgadza się z wcześniejszym wynikiem ręcznego brute-force szukania wskaźników (sekcja "Otwarte pytania") — żadna metoda nie znalazła kodu odwołującego się do tego stringa.

**Wniosek z całej sesji:** to jest realna granica tego, co da się wycisnąć z samej statycznej analizy `z3app.bin` bez znanego adresu bazowego ładowania. Żeby pójść dalej trzeba albo (a) ustalić prawdziwy adres bazowy (np. znajdując dokumentację/inny firmware tej samej rodziny z znanym adresem, albo metodą prób — testując różne adresy bazowe i patrząc czy więcej kodu/XREF-ów "się złoży"), albo (b) zdobyć dump bootloadera przez SWD, który być może zawiera wskazówki (np. jak sam bootloader interpretuje/rebazuje ten plik przy flashowaniu).

### Krok 4 — Jeśli krok 1 wypadnie negatywnie (brak glifów)

Trzeba będzie:
1. Znaleźć dokładny format i lokalizację bitmapy fontu (rozmiar glifu, bpp, offset tabeli).
2. Wygenerować nowe bitmapy dla 18 polskich znaków (np. renderując istniejący krój z urządzenia albo dorabiając zgodny styl).
3. Wstrzyknąć je we wolne miejsce w pliku (albo rozszerzyć plik, jeśli bootloader na to pozwala) i zaktualizować tabelę indeksu, żeby wskazywała na nowe bitmapy.

To wymaga już solidnej znajomości formatu bitmapy — możliwe, ale znacznie więcej pracy niż podmiana tekstu.

---

## 7. Otwarte pytania / niepewności

- **Czy chiński tradycyjny (繁體) jest faktycznie wybieralny z menu**, czy to martwy kod / relikt współdzielonej biblioteki? Jeśli wybieralny — to najlepszy kandydat na podmianę na polski (nikt nie straci używanej funkcji).
- **Struktura wpisu menu wygląda na coś więcej niż "tekst + null"** — bezpośrednio po tekście (np. po "播放界面" pod `0xB7959`) występują 1-2 wartości wyglądające jak wskaźniki flash (`0x0812xxxx`, `0x080Exxxx`/`0x080Fxxxx`). Może to być wskaźnik do ikony, callback funkcji obsługującej dany ekran, albo coś innego — **nieznane bez dezasemblacji**.
- **Nie znaleziono standardowej tablicy wektorów przerwań ARM** na początku pliku — oznacza to, że coś w procesie budowania/pakowania tego obrazu różni się od "podręcznikowego" STM32 bin. Nie blokuje edycji tekstu, ale utrudnia pewne rodzaje analizy (np. jednoznaczne wyznaczenie adresu bazowego ładowania).
- **Nie potwierdzono obecności bitmap glifów** dla polskich znaków — patrz Krok 1.

---

## 8. Przydatne materiały zewnętrzne

- [Wątek ZiShan Z3 na Head-Fi.org](https://www.head-fi.org/threads/zishan-z3-hi-fi-player-thread.911846/) — dyskusja o sprzęcie, wersjach DAC
- [GitHub: SL-RU/osfi-z](https://github.com/SL-RU/osfi-z) — otwarte firmware dla Zishan Z1/Z2 (inny chip, ale ten sam producent/rodzina — potwierdza że Z1/Z2 nie mają wyświetlacza, stąd firmware Z2 mimo posiadania tej samej tabeli czcionek jej nie wykorzystuje)
- [4PDA: Zishan Z1/Z2/Z3](https://4pda.to/forum/index.php?showtopic=842528) — rosyjskie forum, potencjalnie dyskusje o modyfikacjach
- [zishan.ru](http://zishan.ru/) — rosyjska strona fanowska o Zishan (nie udało się automatycznie pobrać treści — strona nie odpowiada na HTTPS; warto sprawdzić manualnie w przeglądarce)
- Wg wyszukiwania: **oficjalnie nie istnieje rosyjska lokalizacja menu** dla Z3 (tylko chiński/angielski) — czyli społeczność rosyjska najpewniej ma ten sam problem/potrzebę co Ty, ale nie znaleziono dowodu na gotowe rozwiązanie.

---

## 9. Struktura tego repozytorium

```
zishan-fimrware/
├── ZiShan_Z3_0.5.rar          # oryginalne archiwum (nietknięte)
├── extracted_z3/z3app.bin     # rozpakowane firmware Z3 (główny cel analizy, poza git - patrz .gitignore)
├── docs/
│   └── ANALIZA.md             # ten dokument
└── tools/
    ├── find_gbk_strings.py    # szuka chińskich (GBK) fragmentów tekstu w binarce
    ├── dump_string_table.py   # odczytuje sekwencje stringów ASCII+GBK w danym zakresie
    ├── dump_charset_table.py  # sprawdza tabelę punktów kodowych Unicode / polskie znaki
    └── wyniki/                # zrzuty wynikow z analizy
```
