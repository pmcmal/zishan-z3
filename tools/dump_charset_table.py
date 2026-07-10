"""
Odczytuje tabele punktow kodowych Unicode (UTF-16LE, 2 bajty/wpis) uzywana
przez silnik czcionek. W firmware Z3 znaleziona pod adresem 0xb7c46-0xb8002.
Wypisuje wszystkie punkty kodowe + sprawdza obecnosc polskich znakow diakrytycznych.

Uzycie: python dump_charset_table.py <plik.bin> <start_hex> <end_hex>
"""
import sys

POLSKIE_ZNAKI = {
    0x0104: 'A z ogonkiem (wielkie)', 0x0105: 'a z ogonkiem (male)',
    0x0106: 'C z kreska (wielkie)',   0x0107: 'c z kreska (male)',
    0x0118: 'E z ogonkiem (wielkie)', 0x0119: 'e z ogonkiem (male)',
    0x0141: 'L z kreska (wielkie)',   0x0142: 'l z kreska (male)',
    0x0143: 'N z kreska (wielkie)',   0x0144: 'n z kreska (male)',
    0x00D3: 'O z kreska (wielkie)',   0x00F3: 'o z kreska (male)',
    0x015A: 'S z kreska (wielkie)',   0x015B: 's z kreska (male)',
    0x0179: 'Z z kreska (wielkie)',   0x017A: 'z z kreska (male)',
    0x017B: 'Z z kropka (wielkie)',   0x017C: 'z z kropka (male)',
}

def main():
    path = sys.argv[1]
    start = int(sys.argv[2], 16)
    end = int(sys.argv[3], 16)
    with open(path, 'rb') as f:
        data = f.read()

    codepoints = []
    i = start
    while i < end:
        cp = data[i] | (data[i+1] << 8)
        codepoints.append(cp)
        i += 2

    print(f"Liczba punktow kodowych: {len(codepoints)}")
    print(f"Zakres w pliku: 0x{start:06x} - 0x{end:06x} ({end-start} bajtow)\n")

    print("Sprawdzenie polskich znakow diakrytycznych:")
    missing = []
    for cp, name in sorted(POLSKIE_ZNAKI.items()):
        if cp in codepoints:
            idx = codepoints.index(cp)
            print(f"  U+{cp:04X} ({name}): obecny, indeks {idx}")
        else:
            missing.append(cp)
            print(f"  U+{cp:04X} ({name}): BRAK")

    if not missing:
        print("\n=> Wszystkie polskie znaki diakrytyczne SA w tabeli punktow kodowych.")
    else:
        print(f"\n=> Brakuje {len(missing)} znakow.")

if __name__ == '__main__':
    main()
