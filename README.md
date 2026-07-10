# zishan-z3

Analiza i próba modyfikacji firmware odtwarzacza **ZiShan Z3** (Hi-Fi DAP, STM32F427 + DAC CS43198/ES9038) — głównie w kierunku dodania/podmiany tekstu menu na polski.
Analysis and modification attempt of the **ZiShan Z3** DAP firmware (Hi-Fi player, STM32F427 + CS43198/ES9038 DAC) — mainly aimed at adding/replacing menu text with Polish.

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

🟡 **W trakcie analizy.** Namierzone i zmapowane wszystkie stringi UI (menu, błędy, formaty audio) oraz tabela znaków Unicode silnika czcionek. Testy na żywym urządzeniu potwierdziły, że:

- ✅ ASCII (angielski) — działa bez problemu
- ✅ Chiński (GBK, uproszczony + tradycyjny) — działa bez problemu
- ❌ Polskie znaki diakrytyczne (ą ć ę ł ń ó ś ź ż) — **nie działają w praktyce** (mimo że są zarejestrowane w tabeli czcionek), wyświetla się `?` i plik się nie odtwarza
- 🛑 **Bootloader waliduje sumę kontrolną pliku** — nawet 1 zmieniony bajt powoduje zawieszenie na "Checking bin" (potwierdzone testem). Algorytm nieznany, wymaga dezasemblacji (Ghidra) do dalszej pracy nad edycją tekstu

Pełne, szczegółowe znaleziska: **[docs/ANALIZA.md](docs/ANALIZA.md)**

### Co już wiadomo

| Pytanie | Status |
|---|---|
| Chip | STM32F427 (ARM Cortex-M4) |
| DAC | CS43198 / ES9038 (wariant sprzętowy) |
| Szyfrowanie firmware? | Nie wykryto |
| Lokalizacja tekstu menu | Znaleziona (`0xB90F7`–`0xB9834` w `z3app.bin` v0.5) |
| Polski z ogonkami (ą, ć, ę...) | Potwierdzone testem: **nie działa** — wymaga patcha kodu + prawdopodobnie nowych bitmap fontu |
| Polski bez ogonków (Jezyk, Ustawienia...) | Realistyczne — czyste ASCII już działa, wymaga tylko bezpiecznej podmiany tekstu |

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
- [ ] Bezpieczna podmiana testowa jednego stringu (np. `"English"` → `"Polski"`)
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

🟡 **Analysis in progress.** All UI strings (menu, errors, audio formats) and the font engine's Unicode character table have been located and mapped. On-device tests confirmed:

- ✅ ASCII (English) — works fine
- ✅ Chinese (GBK, simplified + traditional) — works fine
- ❌ Polish diacritics (ą ć ę ł ń ó ś ź ż) — **don't actually work** (even though they're registered in the font's character table) — displays `?` and the file won't even play

Full detailed findings: **[docs/ANALIZA.md](docs/ANALIZA.md)** (in Polish — will be translated if there's interest)

### What's known so far

| Question | Status |
|---|---|
| Chip | STM32F427 (ARM Cortex-M4) |
| DAC | CS43198 / ES9038 (hardware variant) |
| Firmware encrypted? | No evidence found |
| Menu text location | Found (`0xB90F7`–`0xB9834` in `z3app.bin` v0.5) |
| Polish with diacritics (ą, ć, ę...) | Confirmed by test: **doesn't work** — needs a code patch + likely new font glyph bitmaps |
| Polish without diacritics (Jezyk, Ustawienia...) | Realistic — plain ASCII already works, just needs safe text substitution |

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

- [ ] Disassembly (Ghidra) — find the code responsible for Unicode → internal encoding conversion and text rendering
- [ ] Check whether Traditional Chinese is actually selectable from the menu (candidate slot to repurpose for Polish)
- [ ] Safe test substitution of a single string (e.g. `"English"` → `"Polski"`)
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
