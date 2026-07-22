# zishan-z3

Analiza i próba modyfikacji firmware odtwarzacza **ZiShan Z3** (Hi-Fi DAP, STM32F427 + DAC CS43198/ES9038) — głównie w kierunku dodania/podmiany tekstu menu na polski.
Analysis and modification attempt of the **ZiShan Z3** DAP firmware (Hi-Fi player, STM32F427 + CS43198/ES9038 DAC) — mainly aimed at adding/replacing menu text with Polish.

<img width="490" height="408" alt="images" src="https://github.com/user-attachments/assets/4b0b3b12-bbd7-4d90-b4e0-3ba825b1e9bc" />


---

<details open>
<summary><strong>🇵🇱 Polski</strong> (kliknij, aby zwinąć/rozwinąć)</summary>

> ⚠️ **Uwaga / Disclaimer**
> To jest projekt eksploracyjny (reverse engineering) prowadzony na własnym sprzęcie. Modyfikacja firmware zawsze niesie ryzyko (w najgorszym wypadku: brick urządzenia). Rób to na własną odpowiedzialność, miej zawsze zapasową kopię oryginalnego firmware, i najlepiej sprawdź czy Twoje urządzenie ma jakiś tryb "recovery" (np. przycisk + reset) zanim zaczniesz flashować zmodyfikowane pliki.
>
> To repozytorium zawiera oryginalne pliki firmware (`.rar`) używane do analizy — Zishan nie ma realnej oficjalnej strony/kanału dystrybucji (firmware krąży przez fora i Baidu, linki bywają niestabilne), więc trzymam je tu dla archiwizacji. Jeśli jesteś posiadaczem praw i chcesz, żebym je usunął — daj znać.

### Spis treści

- [Status projektu](#status-projektu)
- [Co już wiadomo](#co-już-wiadomo)
- [Struktura repo](#struktura-repo)
- [Jak zacząć](#jak-zacząć)
- [Plany / TODO](#plany--todo)
- [Materiały zewnętrzne](#materiały-zewnętrzne)

### Status projektu

🛑 **Zapauzowane — zablokowane sprzętowo.** Statyczna analiza pliku firmware doszła do realnej granicy — dalszy postęp wymaga dumpu flash przez SWD (debugger + gołe punkty testowe na płycie), nie samej analizy plików. Zapisane tu jako punkt startowy dla kogoś (może Ciebie?), kto ma taki debugger i chce pociągnąć dalej.

Co ustalono, w skrócie (pełne szczegóły: **[docs/ANALIZA.md](docs/ANALIZA.md)**):

- ✅ Zmapowane wszystkie stringi UI (menu, błędy, formaty audio) i tabela znaków Unicode silnika czcionek
- ✅ ASCII (angielski) i chiński (GBK, uproszczony + tradycyjny) w nazwach plików — działają bez problemu na urządzeniu
- ❌ Polskie znaki diakrytyczne (ą ć ę ł ń ó ś ź ż) — **nie działają w praktyce** (mimo że są zarejestrowane w tabeli czcionek silnika), wyświetla się `?` i plik się nie odtwarza
- 🛑 **Bootloader waliduje sumę kontrolną pliku przed flashowaniem** — nawet 1 zmieniony bajt powoduje zawieszenie na "Checking bin" (potwierdzone testem na urządzeniu — oryginał flashuje się gładko, zmodyfikowany plik wisi). Wypróbowano CRC32/CRC16/Fletcher16/Adler32/proste sumy — żaden nie zgadza się z obserwowaną wartością
- 🛑 **Kod bootloadera (ten, który liczy checksum) nie jest częścią pliku `z3app.bin`** — potwierdzone (żadne z jego komunikatów nie istnieją jako stringi w tym pliku). Żyje w osobnym, niedostępnym regionie flash STM32
- 🛑 **Analiza w Ghidrze (import ARM:LE:32:Cortex) potwierdza realny kod Thumb w pliku**, ale bez znanego adresu bazowego ładowania nie da się automatycznie znaleźć, co odwołuje się do stringów menu — auto-analiza + "ARM Aggressive Instruction Finder" znalazły tylko ~10-20 funkcji w pliku 760KB

**Co by odblokowało dalszą pracę:** dump całej flashy STM32F427 przez SWD (ST-Link + punkty testowe na płycie) — dałoby to zarówno kod bootloadera z algorytmem checksumy, jak i prawdziwy adres bazowy do dalszej analizy kodu aplikacji. Wymaga sprzętu (debugger) i sprawdzenia czy nie jest włączone RDP (ochrona odczytu).

### Co już wiadomo

| Pytanie | Status |
|---|---|
| Chip | STM32F427 (ARM Cortex-M4) |
| DAC | CS43198 / ES9038 (wariant sprzętowy) |
| Szyfrowanie firmware? | Nie wykryto (ale JEST walidacja checksumy — patrz wyżej) |
| Lokalizacja tekstu menu | Znaleziona (`0xB90F7`–`0xB9834` w `z3app.bin` v0.5) |
| Bezpieczna podmiana tekstu (bez zmiany długości) | Metoda działa technicznie (zweryfikowana bit-po-bicie), ale **nie da się przetestować na urządzeniu** bez najpierw rozwiązania checksumy |
| Polski z ogonkami (ą, ć, ę...) | Potwierdzone testem: **nie działa** — wymaga patcha kodu + prawdopodobnie nowych bitmap fontu |
| Polski bez ogonków (Jezyk, Ustawienia...) | Technicznie przygotowane (skrócone etykiety: Ust/Syst/Jez/Wers/Info), ale zablokowane tym samym problemem checksumy |

Szczegóły, metodologia i dowody: [docs/ANALIZA.md](docs/ANALIZA.md).

### Struktura repo

```
.
├── ZiShan_Z3_0.5.rar       # oryginalne firmware Z3 (cel analizy)
├── docs/
│   └── ANALIZA.md          # pełna analiza: mapa pliku, znalezione stringi, testy, plan działania
└── tools/
    ├── find_gbk_strings.py    # szuka fragmentów chińskiego tekstu (GBK) w binarce
    ├── dump_string_table.py   # odczytuje sekwencje stringów ASCII+GBK w danym zakresie
    ├── dump_charset_table.py  # sprawdza tabelę punktów kodowych Unicode / polskie znaki
    └── wyniki/                 # zrzuty z analizy (surowe listy znalezionych stringów)
```

Wypakowany `z3app.bin` (`extracted_z3/`) nie jest w repo (patrz `.gitignore`) — to tylko rozpakowana zawartość `.rar`, każdy sobie to odtworzy w 5 sekund.

### Jak zacząć

1. Wypakuj `ZiShan_Z3_0.5.rar` → `z3app.bin` (np. 7-Zip).
2. Odpal skrypty z `tools/`, np.:
   ```
   python tools/find_gbk_strings.py z3app.bin wyniki.txt
   python tools/dump_string_table.py z3app.bin b6000 b9dfb wyniki2.txt
   python tools/dump_charset_table.py z3app.bin b7c46 b8002
   ```
3. Przeczytaj [docs/ANALIZA.md](docs/ANALIZA.md) — tam jest pełna mapa pliku i lista znalezionych offsetów.

### Plany / TODO

- [ ] Dezasemblacja (Ghidra) — znaleźć kod odpowiedzialny za konwersję Unicode → wewnętrzne kodowanie i renderowanie tekstu
- [ ] Sprawdzić, czy chiński tradycyjny jest faktycznie wybieralny z menu (kandydat na podmianę na polski)
- [x] Bezpieczna podmiana testowa jednego stringu (`"English"` → `"Polski"`) — technicznie gotowa, zablokowana checksumą
- [x] Zmierzony budżet bajtowy dla 5 kolejnych etykiet menu, przygotowane skrócone podmiany (Ust/Syst/Jez/Wers/Info)
- [x] Sesja w Ghidrze — potwierdzone realne granice analizy bez znanego adresu bazowego
- [ ] **Zablokowane bez sprzętu:** dump flash przez SWD, żeby znaleźć algorytm checksumy i prawdziwy adres bazowy
- [ ] Ocena: czy da się dodać realne bitmapy glifów dla ą/ć/ę/ł/ń/ó/ś/ź/ż
- [ ] Pełne tłumaczenie menu na polski (najpierw bez ogonków, potem — jeśli się uda — z ogonkami)

### Materiały zewnętrzne

- [Wątek ZiShan Z3 na Head-Fi.org](https://www.head-fi.org/threads/zishan-z3-hi-fi-player-thread.911846/)
- [GitHub: SL-RU/osfi-z](https://github.com/SL-RU/osfi-z) — otwarte firmware dla Zishan Z1/Z2
- [4PDA: Zishan Z1/Z2/Z3](https://4pda.to/forum/index.php?showtopic=842528)
- [zishan.ru](http://zishan.ru/) — rosyjska strona fanowska

</details>

<details>
<summary><strong>🇬🇧 English</strong> (click to expand/collapse)</summary>

> ⚠️ **Disclaimer**
> This is an exploratory reverse-engineering project done on my own hardware. Firmware modification always carries risk (worst case: bricking the device). Do this at your own risk, always keep a backup of the original firmware, and ideally check whether your device has some kind of "recovery" mode (e.g. button + reset) before flashing modified files.
>
> This repository includes the original firmware files (`.rar`) used for the analysis — Zishan doesn't really have an official website/distribution channel (firmware circulates through forums and Baidu, links tend to rot), so I'm keeping them here for archival purposes. If you're a rights holder and want them removed, let me know.

### Table of contents

- [Project status](#project-status)
- [What's known so far](#whats-known-so-far)
- [Repo structure](#repo-structure)
- [Getting started](#getting-started)
- [Plans / TODO](#plans--todo)
- [External resources](#external-resources)

### Project status

🛑 **Paused — blocked on hardware access.** Static analysis of the firmware file has hit a real ceiling — further progress needs a flash dump via SWD (debug probe + bare test points on the board), not more file analysis. Left here as a starting point for whoever (maybe you?) has a debug probe and wants to push further.

What's been established, in short (full details: **[docs/ANALIZA.md](docs/ANALIZA.md)**, in Polish — will be translated if there's interest):

- ✅ All UI strings (menu, errors, audio formats) and the font engine's Unicode character table are mapped
- ✅ ASCII (English) and Chinese (GBK, simplified + traditional) in filenames — work fine on the device
- ❌ Polish diacritics (ą ć ę ł ń ó ś ź ż) — **don't actually work** (even though they're registered in the font's character table) — displays `?` and the file won't even play
- 🛑 **The bootloader validates a checksum of the whole file before flashing** — even 1 changed byte causes it to hang on "Checking bin" (confirmed on real hardware — the original flashes cleanly, the modified file hangs). Tried CRC32/CRC16/Fletcher16/Adler32/simple sums — none match the observed value
- 🛑 **The bootloader code (the one computing the checksum) is not part of `z3app.bin`** — confirmed (none of its on-screen messages exist as strings in this file). It lives in a separate, inaccessible flash region
- 🛑 **Ghidra analysis (imported as ARM:LE:32:Cortex) confirms real Thumb code in the file**, but without a known load base address, there's no automatic way to find what references the menu strings — auto-analysis + the "ARM Aggressive Instruction Finder" only found ~10-20 functions in a 760KB file

**What would unblock further work:** a full flash dump of the STM32F427 via SWD (ST-Link + test points on the board) — this would yield both the bootloader code (with the checksum algorithm) and the true load base address for further code analysis. Needs hardware (a debug probe) and checking whether readout protection (RDP) is enabled.

### What's known so far

| Question | Status |
|---|---|
| Chip | STM32F427 (ARM Cortex-M4) |
| DAC | CS43198 / ES9038 (hardware variant) |
| Firmware encrypted? | No evidence found (but there IS checksum validation — see above) |
| Menu text location | Found (`0xB90F7`–`0xB9834` in `z3app.bin` v0.5) |
| Safe text substitution (same byte length) | Method works technically (verified bit-for-bit), but **can't be tested on the device** until the checksum is solved |
| Polish with diacritics (ą, ć, ę...) | Confirmed by test: **doesn't work** — needs a code patch + likely new font glyph bitmaps |
| Polish without diacritics (Jezyk, Ustawienia...) | Technically prepared (shortened labels: Ust/Syst/Jez/Wers/Info), but blocked by the same checksum issue |

Details, methodology and evidence: [docs/ANALIZA.md](docs/ANALIZA.md) (PL).

### Repo structure

```
.
├── ZiShan_Z3_0.5.rar       # original Z3 firmware (analysis target)
├── docs/
│   └── ANALIZA.md          # full analysis: file map, found strings, tests, action plan (Polish)
└── tools/
    ├── find_gbk_strings.py    # finds Chinese (GBK) text fragments in the binary
    ├── dump_string_table.py   # reconstructs ASCII+GBK string sequences in a given range
    ├── dump_charset_table.py  # checks the Unicode code point table / Polish character support
    └── wyniki/                 # ("results") raw dumps from the analysis
```

The unpacked `z3app.bin` (`extracted_z3/`) is not in the repo (see `.gitignore`) — it's just the unpacked contents of the `.rar`, anyone can regenerate it in 5 seconds.

### Getting started

1. Unpack `ZiShan_Z3_0.5.rar` → `z3app.bin` (e.g. with 7-Zip).
2. Run the scripts in `tools/`, e.g.:
   ```
   python tools/find_gbk_strings.py z3app.bin results.txt
   python tools/dump_string_table.py z3app.bin b6000 b9dfb results2.txt
   python tools/dump_charset_table.py z3app.bin b7c46 b8002
   ```
3. Read [docs/ANALIZA.md](docs/ANALIZA.md) — it has the full file map and list of found offsets (Polish).

### Plans / TODO

- [x] Safe test substitution of a single string (`"English"` → `"Polski"`) — technically ready, blocked by checksum
- [x] Measured byte budget for 5 more menu labels, prepared shortened substitutions (Ust/Syst/Jez/Wers/Info)
- [x] Ghidra session — confirmed the real limits of analysis without a known load base address
- [ ] **Blocked without hardware:** SWD flash dump, to find the checksum algorithm and the true load base address
- [ ] Evaluate whether real glyph bitmaps can be added for ą/ć/ę/ł/ń/ó/ś/ź/ż
- [ ] Full Polish menu translation (first without diacritics, then — if feasible — with them)

### External resources

- [ZiShan Z3 thread on Head-Fi.org](https://www.head-fi.org/threads/zishan-z3-hi-fi-player-thread.911846/)
- [GitHub: SL-RU/osfi-z](https://github.com/SL-RU/osfi-z) — open-source firmware for Zishan Z1/Z2
- [4PDA: Zishan Z1/Z2/Z3](https://4pda.to/forum/index.php?showtopic=842528)
- [zishan.ru](http://zishan.ru/) — Russian fan site

</details>

---

Inny mój projekt modderski (Android, root, DAC) / Another modding project of mine (Android, root, DAC): [oilsky-g88](https://github.com/pmcmal/oilsky-g88)

☕ If I helped, give me a tip, I spent several evenings on it :) https://tipped.pl/pmcmalec
